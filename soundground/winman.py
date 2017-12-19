#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Window manager
Coordinates in (y, x) to be consistent with curses
"""

from soundground import metadata, utils
import curses

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
        Creates a new window, accepting either fixed or relative numbers
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

    def add(self, caption, selectable=True):
        self.items.append({
            'caption': caption,
            'selectable': selectable
        })
        self.draw()

    def remove(self, index):
        self.items.pop(index)
        self.draw()

    def select(self, index, relative=True):
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
        if not self.items[self.selected]['selectable']:
            if not relative:
                return False
            self.selected += index

        # Update scroll position
        height, width = self.window.getmaxyx()
        if self.selected + 1 >= self.scrollpos + height:
            self.scrollpos = self.selected - height + 1
        elif self.selected < self.scrollpos:
            self.scrollpos = self.selected

        self.draw()
