#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Program entry point"""

from __future__ import print_function

import argparse
import sys
import curses

from soundground import metadata, winman

def main(stdscr):
    """
    Program entry point.
    """

    stdscr.clear()

    wg = winman.WindowGroup(stdscr)

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
