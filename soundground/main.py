#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Program entry point"""

import argparse
import sys
import curses
import curses.textpad
import vlc

from soundground import metadata, utils
from soundground import winman as wm
from soundground import command_interpreter
from soundground.winman import Value

def init_nav(navlist):
    """
    Fill left navigation pane
    """
    navlist.add("Stream")
    navlist.add("Charts")
    navlist.add("Discover")

    navlist.add("", False)

    navlist.add("Overview")
    navlist.add("Likes")
    navlist.add("Playlists")
    navlist.add("Albums")
    navlist.add("Stations")
    navlist.add("Following")
    navlist.add("History")


def init_windows(wg):
    # Create windows
    wg.create_window('title', 0, 0, 1, Value(100))
    wg.create_window('nav', 1, 0, Value(100, -2), Value(25))
    wg.create_window('command', Value(100, -1), 0, 1, Value(100))

    # Set title bar style and contents
    wg['title'].bkgd(' ', curses.A_UNDERLINE)
    wg['title'].addstr(0, 0, "Soundground - v{}".format(metadata.version))

    # Left navigation pane
    wg['nav'].border(' ', '|', ' ', ' ', ' ', '|', ' ', '|')
    navlist = wm.SelectableList(wg['nav'])
    init_nav(navlist)
    wg.extra_draws.append(navlist)

    # Command bar and textbox
    wg['command'].bkgd(' ', curses.A_REVERSE)
    commandbox = curses.textpad.Textbox(wg['command'])

    # Return controls
    return {
        'nav': navlist,
        'cmd': commandbox
    }


def main(stdscr):
    """
    Program entry point.
    """

    # Initialize media player
    mp = vlc.MediaPlayer()

    # Initialize screen
    stdscr.clear()
    stdscr.timeout(100)
    wg = wm.WindowGroup(stdscr)
    controls = init_windows(wg)

    # Pass command box control to interpreter
    ci = command_interpreter.Interpreter(controls['cmd'], mp)

    # Create status bar on top of the command bar
    statusline = wm.StatusLine(wg['command'], mp)
    wg.extra_draws.append(statusline)

    # Keep track of active control
    active = 'nav'

    # Force redraw windows
    wg.resize()

    last_command = ''
    while True:
        # Clear command box if not editing
        if ci.done:
            statusline.draw()

        # Read input
        c = stdscr.getch()
        if c == ord('q'):
            # Quit
            statusline.notify("Hold q to quit")
            if stdscr.getch() == ord('q'):
                break

        elif c == ord(':'):
            # Enter command mode
            wg['command'].clear()
            wg['command'].addch(':')
            ci.done = False
            controls['cmd'].edit(ci.validate)

        elif c in {ord('j'), ord('k'), curses.KEY_DOWN, curses.KEY_UP}:
            # Process up/down selection
            if c in {ord('j'), curses.KEY_DOWN}:
                direction = 1
            else:
                direction = -1

            # Send selection change to active control
            if active in controls:
                controls[active].select(direction)

        elif c in {ord('-'), ord('='), ord('+')}:
            # Volume control
            current = mp.audio_get_volume()
            if c == ord('-'):
                current -= 10
            else:
                current += 10

            # Clamp volume levels
            if current > 125:
                current = 125
            if current < 0:
                current = 0

            mp.audio_set_volume(current)

        elif c == ord(' '):
            # Play/pause audio
            if mp.can_pause():
                mp.pause()

        # Check terminal resize
        if c == curses.KEY_RESIZE:
            wg.resize()

    return 0


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(curses.wrapper(main))


if __name__ == '__main__':
    entry_point()
