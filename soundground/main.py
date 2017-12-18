#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Program entry point"""

from __future__ import print_function

import argparse
import sys
import curses

from soundground import metadata, winman, utils
from soundground.winman import Value

def main(stdscr):
    """
    Program entry point.
    """

    # Initialize screen
    stdscr.clear()
    wg = winman.WindowGroup(stdscr)
    
    # Create windows
    wg.create_window('title', 0, 0, 1, Value(100))
    wg.create_window('status', Value(100, -1), 0, 1, Value(100))
    wg.create_window('nav', 1, 0, Value(100, -2), Value(25))

    wg['title'].bkgd(' ', curses.A_UNDERLINE)
    wg['title'].addstr(0, 0, 'Soundground - v0.1')
    wg['nav'].border(' ', '|', ' ', ' ', ' ', '|', ' ', '|')

    wg.resize()

    while True:
        # Read input
        c = stdscr.getch()
        if c == ord('q'):
            break

        # Check terminal resize
        if c == curses.KEY_RESIZE:
            wg.resize()

    return 0


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(curses.wrapper(main))


if __name__ == '__main__':
    entry_point()
