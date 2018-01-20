#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Program entry point"""

import argparse
import sys
import curses
import curses.textpad
import vlc

from soundground import metadata, utils, credman, cloudman
from soundground import winman as wm
from soundground import command_interpreter
from soundground.winman import Value

def refresh_nav(navlist, cred=None):
    """
    Fill left navigation pane
    """

    # Save current selection
    selected_item = navlist.selected

    # Clear the list to prevent duplicates
    navlist.items.clear()

    # Use empty credentials if not given
    if cred == None:
        cred = credman.Credentials()

    # Add buttons
    navlist.add(cred.username, False)
    if cred.username == '':
        navlist.add("Login",    value="login")
    else:
        navlist.add("Logout",   value="logout")

    navlist.add("", False)

    """
    These stuff won't work without auth. SoundCloud uses OAuth for 3rd party
    applications, however since they've closed off the application registration,
    soundground is forced to use youtube-dl, which doesn't support Soundcloud
    authentication yet.

    See https://github.com/rg3/youtube-dl/issues/9272
    """

    # navlist.add("Stream",       value="list stream")
    # navlist.add("Charts",       value="list charts/top")
    # navlist.add("Discover",     value="list discover")

    # navlist.add("", False)

    # navlist.add("Overview",     value="list you/collection")
    navlist.add("Likes",        value="list you/likes")
    navlist.add("Playlists",    value="list you/sets")
    # navlist.add("Albums",       value="list you/albums")
    # navlist.add("Stations",     value="list you/stations")
    # navlist.add("Following",    value="list you/following")
    # navlist.add("History",      value="list you/history")

    # Select list
    navlist.select(selected_item, False)


def init_windows(wg):
    # Create windows
    wg.create_window('title', 0, 0, 1, Value(100))
    wg.create_window('nav', 1, 0, Value(100, -2), Value(25))
    wg.create_window('command', Value(100, -1), 0, 1, Value(100))
    wg.create_window('playlist', 1, Value(25, 1), Value(100, -2), Value(75, -1))

    # Set title bar style and contents
    wg['title'].bkgd(' ', curses.A_UNDERLINE)
    wg['title'].addstr(0, 0, "Soundground - v{}".format(metadata.version))

    # Left navigation pane
    wg['nav'].border(' ', '|', ' ', ' ', ' ', '|', ' ', '|')
    navlist = wm.SelectableList(wg['nav'])
    refresh_nav(navlist)
    navlist.active = True
    wg.extra_draws.append(navlist)

    # Command bar and textbox
    wg['command'].bkgd(' ', curses.A_REVERSE)
    commandbox = curses.textpad.Textbox(wg['command'])

    # Create playlist
    playlist = wm.SelectableList(wg['playlist'])
    wg.extra_draws.append(playlist)

    # Return controls
    return {
        'nav': navlist,
        'cmd': commandbox,
        'playlist': playlist
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

    # Create status bar on top of the command bar
    statusline = wm.StatusLine(wg['command'], mp)
    wg.extra_draws.append(statusline)

    # Keep track of active control
    active_list = ['nav', 'playlist']
    active_index = 0

    # Start credentials manager
    cred = credman.Credentials()
    cred.load()
    refresh_nav(controls['nav'], cred)

    # Initialize SoundCloud manager with credentials
    cm = cloudman.CloudManager(cred, controls['playlist'])

    # Pass command box control to interpreter
    ci_params = {
        'textbox': controls['cmd'],
        'playlist': controls['playlist'],
        'statusline': statusline,
        'player': mp,
        'cred': cred,
        'cloud': cm
    }
    ci = command_interpreter.Interpreter(ci_params)

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
            active = active_list[active_index]
            if active in controls:
                controls[active].select(direction)

        elif c == 9:
            # Tab to toggle list selection
            if active_index < len(active_list) - 1:
                active_index += 1
            else:
                active_index = 0

            # Deactivate all lists
            for control in active_list:
                controls[control].active = False
                controls[control].draw()

            # Activate active list
            active = controls[active_list[active_index]]
            active.active = True
            active.draw()

        elif c == 10:
            # Enter to confirm selection
            active = active_list[active_index]
            index = controls[active].selected
            item = controls[active].items[index]
            if active == 'nav':
                # Select nav item
                ci.execute(item['value'])
                refresh_nav(controls['nav'], cred)

        elif c in {ord('-'), ord('='), ord('+')}:
            # Volume control
            current = mp.audio_get_volume()
            if c == ord('-'):
                current -= 10
            else:
                current += 10

            # Clamp volume levels
            if current > 150:
                current = 150
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
