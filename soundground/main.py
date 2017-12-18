#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Program entry point"""

from __future__ import print_function

import argparse
import sys
import curses
import curses.textpad

from soundground import metadata, winman, utils
from soundground import command_interpreter
from soundground.winman import Value

def main(stdscr):
    """
    Program entry point.
    """

    # Initialize screen
    stdscr.clear()
    stdscr.timeout(100)
    wg = winman.WindowGroup(stdscr)
    ci = command_interpreter.Interpreter()
    
    # Create windows
    wg.create_window('title', 0, 0, 1, Value(100))
    wg.create_window('nav', 1, 0, Value(100, -2), Value(25))
    wg.create_window('command', Value(100, -1), 0, 1, Value(100))

    # Set title bar style and contents
    wg['title'].bkgd(' ', curses.A_UNDERLINE)
    wg['title'].addstr(0, 0, 'Soundground - v{}'.format(metadata.version))
    # Left navigation pane
    wg['nav'].border(' ', '|', ' ', ' ', ' ', '|', ' ', '|')
    # Command bar and textbox
    wg['command'].bkgd(' ', curses.A_REVERSE)
    commandbox = curses.textpad.Textbox(wg['command'])

    wg.resize()

    last_command = ''
    while True:
        # Check command box
        if commandbox.gather() != last_command:
            # New command was entered
            last_command = commandbox.gather()
            wg['command'].clear()
            ci.execute(last_command)

        # Read input
        c = stdscr.getch()
        if c == ord('q'):
            # Quit
            break
        elif c == ord(':'):
            # Enter command mode
            wg['command'].clear()
            wg['command'].addch(':')
            commandbox.edit()

        # Check terminal resize
        if c == curses.KEY_RESIZE:
            wg.resize()

    return 0


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(curses.wrapper(main))


if __name__ == '__main__':
    entry_point()
