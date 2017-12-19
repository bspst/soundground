#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Command Interpreter
Runs commands
"""

class Interpreter(object):
    def __init__(self, textbox):
        self.history = []
        self.textbox = textbox
        self.done = False

    def is_done(self):
        # Returns whether the text box can be safely cleared
        if self.done:
            self.done = False
            return True

        return False

    def validate(self, keycode):
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
        cmd = self.textbox.gather()[1:].strip()

        if cmd == 'q' or cmd == 'quit':
            raise SystemExit(0)
