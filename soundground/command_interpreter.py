#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Command Interpreter
Runs commands
"""

class Interpreter(object):
    def __init__(self, textbox, statusline, player, cred):
        self.history = []
        self.textbox = textbox
        self.statusline = statusline
        self.player = player
        self.cred = cred
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

    def execute(self, cmdstr=None):
        """
        Runs a command
        """
        if cmdstr == None:
            cmd = self.textbox.gather()[1:].strip().split()
        else:
            cmd = cmdstr.split()

        if cmd[0] == 'q' or cmd[0] == 'quit':
            raise SystemExit(0)
        elif cmd[0] == 'playurl':
            # Play custom audio file by URL
            self.player.set_mrl(cmd[1])
            self.player.play()
        elif cmd[0] == 'login':
            # Show login prompt
            self.cred.username = self.statusline.prompt("Username: ")
            self.cred.password = self.statusline.prompt("Password: ", True)
            savecreds = self.statusline.prompt("Save credentials (y/N)? ")
            if len(savecreds) > 0 and savecreds[0].lower() == 'y':
                self.cred.save()
            self.statusline.draw()
