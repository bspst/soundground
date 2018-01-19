#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Window manager
Coordinates in (y, x) to be consistent with curses
"""

from soundground import metadata, utils
import curses
import time

class Value(object):
    """
    Defines a number used for relative calculations
    """
    def __init__(self, percent_value, absolute_bias=0):
        self.value = percent_value
        self.bias = absolute_bias

    def apply(self, target):
        """
        Applies the percentage value to a target
        """
        if type(self) is Value:
            return int(round((self.value / 100) * target) + self.bias)
        else:
            return int(round(self))

class WindowGroup(object):
    """
    A group of windows
    """
    def __init__(self, stdscr):
        """
        Initialization
        """

        self.windows = {}
        self.stdscr = stdscr
        self.extra_draws = []

    def __getitem__(self, name):
        """
        Returns a window by its name
        """
        return self.windows[name].window

    def draw(self):
        """
        Refresh all windows
        """

        self.stdscr.clear()
        for name in self.windows:
            window = self.windows[name].window
            window.overwrite(self.stdscr)
            window.noutrefresh()

        # Also refresh extra stuff (e.g. SelectableList)
        for instance in self.extra_draws:
            instance.draw()

        curses.doupdate()

    def resize(self):
        """
        Resizes windows based on their percent values
        """

        curses.endwin()
        height, width = self.stdscr.getmaxyx()
        self.stdscr.move(height - 1, 0)

        for name in self.windows:
            window = self.windows[name]
            window.resize(height, width)

        self.draw()

    def create_window(self, name, y, x, h, w):
        """
        Creates a new window, accepting either integer or Value
        """

        if name in self.windows:
            raise Exception("Window exists!")

        ymax, xmax = (curses.LINES, curses.COLS)

        self.windows[name] = RelativeWindow(y, x, h, w, self.stdscr)

class RelativeWindow(object):
    """
    Windows with relative sizes
    """

    def __init__(self, y, x, h, w, stdscr):
        """
        Initialize sizes
        """
        self.y = y
        self.x = x
        self.h = h
        self.w = w

        self.window = curses.newwin(1, 1, 0, 0)
        ymax, xmax = stdscr.getmaxyx()
        self.resize(ymax, xmax)
        pass

    def resize(self, height, width):
        """
        Resize window based on actual size
        """
        new_y = Value.apply(self.y, height)
        new_x = Value.apply(self.x, width)
        new_height = Value.apply(self.h, height)
        new_width = Value.apply(self.w, width)

        self.window.resize(new_height, new_width)
        self.window.mvwin(new_y, new_x)

class SelectableList(object):
    """
    Implements a scrollable list with selectable items
    """
    def __init__(self, window):
        self.window = window
        self.items = []
        self.selected = 0
        self.scrollpos = 0

    def draw(self):
        """
        Redraw list
        """
        self.window.clear()
        height, width = self.window.getmaxyx()
        for offset in range(height):
            index = self.scrollpos + offset
            if index >= len(self.items):
                # No more items to draw
                break

            item = self.items[index]
            # Change background for selected item
            attr = curses.A_REVERSE if index == self.selected else curses.A_NORMAL
            padded = item['caption'].ljust(width)
            try:
                self.window.addstr(offset, 0, padded, attr)
            except:
                pass
        self.window.refresh()

    def add(self, caption, selectable=True, value=None):
        """
        Add an item to the list and draws it

        An item is a map with the following keys:
        - caption:    the text displayed on the list
        - selectable: if False, the item will skip selection
        - value:      a custom value, could be used to specify a command to be
                      executed when selected
        """

        if value == None:
            value = caption

        self.items.append({
            'caption': caption,
            'selectable': selectable,
            'value': value
        })
        self.draw()

    def remove(self, index):
        """
        Remove an item by its index
        """
        self.items.pop(index)
        self.draw()

    def select(self, index, relative=True):
        """
        Highlight an item by its index. If relative, the current selection index
        will be incremented by the index parameter instead of being set.
        """
        if relative:
            self.selected += index
        else:
            self.selected = index

        # Make sure selection doesn't go out of bounds
        if self.selected < 0:
            self.selected = 0
        elif self.selected >= len(self.items):
            self.selected = len(self.items) - 1

        # Skip unselectable items
        while not self.items[self.selected]['selectable']:
            if not relative:
                return False
            self.selected += index

            # Prevent overflow
            if self.selected < 0 or self.selected >= len(self.items):
                self.selected -= 2 * index

        # Update scroll position
        height, width = self.window.getmaxyx()
        if self.selected + 1 >= self.scrollpos + height:
            self.scrollpos = self.selected - height + 1
        elif self.selected < self.scrollpos:
            self.scrollpos = self.selected

        self.draw()


class StatusLine(object):
    """
    Manages the bottom status bar text
    """

    SYM_PLAY = u"\u25B6"
    SYM_PAUSE = u"\u23F8"

    def __init__(self, window, player):
        self.window = window
        self.player = player
        self.override_text = None
        self.override_cycles = 0

        self.prompting = False
        self.prompt_hidden = False
        self.prompt_value = ''

    def draw(self):
        """
        Redraw status bar
        """
        self.window.erase()

        # Fetch some parameters
        playing = self.SYM_PLAY if self.player.is_playing() else self.SYM_PAUSE
        title = self.player.get_title()
        t_total = utils.format_millis(self.player.get_length())
        t_now = utils.format_millis(self.player.get_position() * self.player.get_length())
        vol = self.player.audio_get_volume()

        # Format params
        text = "[ {} ] {} [{}/{}] | Vol: {}"
        formatted = text.format(playing, title, t_now, t_total, vol)

        # Override status text if present
        if self.override_text != None and self.override_cycles > 0:
            formatted = self.override_text
            self.override_cycles -= 1

        # Draw to screen
        try:
            self.window.addstr(0, 0, formatted)
            self.window.refresh()
        except:
            pass

    def notify(self, text):
        """
        Shows text in the status bar until next refresh or manually dismissed
        """
        self.override_text = text
        self.override_cycles = 30
        self.draw()

    def dismiss(self):
        """
        Dismiss notification text
        """
        self.override_cycles = 0
        self.draw()

    def prompt(self, text, hidden=False):
        """
        Prompts the user for input
        Keystrokes will be hidden if hidden is True
        """
        import curses.textpad

        self.prompting = True
        self.prompt_hidden = hidden

        self.window.clear()
        try:
            self.window.addstr(0, 0, text)
            self.window.refresh()
        except:
            pass

        box = curses.textpad.Textbox(self.window)
        box.edit(self._prompt_validator)

        while self.prompting:
            # Block until user finishes input
            time.sleep(0.1)

        if hidden:
            return self.prompt_value
        else:
            return box.gather()[len(text):].strip()

    def _prompt_validator(self, char):
        """
        Listens for keystrokes on prompt
        """
        if char == 10:
            # Line feed (Enter/Return)
            self.prompting = False
            return char

        # If hidden (password mode)
        if self.prompt_hidden:
            if char == curses.KEY_BACKSPACE:
                # Backspace
                self.prompt_value = self.prompt_value[:-1]
                return char

            if char < 32 or char > 126:
                # Only allow printable characters
                return 0

            self.prompt_value += chr(char)
            # Replace printable characters with asterisks
            return ord('*')

        self.prompt_value = ''

        return char
