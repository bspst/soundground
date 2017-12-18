#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Window manager
"""

from soundground import metadata, utils
import curses

class WindowGroup(object):
    """
    Resizes windows
    """
    def __init__(self, stdscr):
        """
        Initialization
        """

        self.windows = {}
        self.stdscr = stdscr

    def resize(self):
        """
        Resizes windows based on their percent values
        """

        height, width = self.stdscr.getmaxyx()

        for name in self.windows:
            window = self.windows[name]
            window.resize(height, width)

    def new(self, name, y, x, h, w):
        """
        Create a new window with x, y, width, and height in percent
        """

        if name in self.windows:
            raise Exception("Window exists!")

        self.windows[name] = RelativeWindow(y, x, h, w)

class RelativeWindow(object):
    """
    Windows with relative sizes
    """

    def __init__(self, y, x, h, w):
        """
        Initialize sizes in percent
        """
        self.y = y
        self.x = x
        self.h = h
        self.w = w
        self.window = curses.newwin(1, 1, 0, 0)
        pass

    def resize(self, height, width):
        """
        Resize window based on actual size
        """
        self.window.resize(int(height*self.h), int(width*self.w))
        self.window.mvwin(int(height*self.y), int(width*self.x))

class TitleBar(object):
    """
    Handles the title bar
    """

    def __init__(self, window):
        self.window = window
        self.w, self.h = window.getmaxyx()

    def draw():
        """
        Draws to the window
        """

        title_text = "Soundground v{}".format(metadata.version)
        title_x = utils.center_text(self.w, title_text)
        stdscr.addstr(0, int(title_x), title_text)
