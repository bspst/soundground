#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Command Interpreter
Runs commands
"""

class Interpreter(object):
    def __init__(self, textbox, player):
        self.history = []
        self.textbox = textbox
        self.player = player
        self.done = False

    def validate(self, keycode):
        self.done = False

        if keycode == 27:
            # Map Escape to Ctrl-G (BEL), which terminates the editing sesson
            self.done = True
            return 7
        elif keycode == 10:
            # Line feed, execute command
            self.done = True
            self.execute()

        return keycode

    def execute(self):
        cmd = self.textbox.gather()[1:].strip().split()

        if cmd[0] == 'q' or cmd[0] == 'quit':
            raise SystemExit(0)
        elif cmd[0] == 'playurl':
            # Play custom audio file by URL
            self.player.set_mrl(cmd[1])
            self.player.play()
