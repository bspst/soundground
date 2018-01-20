#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Command Interpreter
Runs commands
"""

class Interpreter(object):
    def __init__(self, params):
        self.history = []
        self.textbox = params['textbox']
        self.playlist = params['playlist']
        self.statusline = params['statusline']
        self.player = params['player']
        self.cred = params['cred']
        self.cloudman = params['cloud']
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
            # Check if logged in
            if self.cred.username != '':
                self.statusline.notify("Already logged in as {}".format(self.cred.username))
                return False
            # Show login prompt
            self.cred.username = self.statusline.prompt("Username: ")
            self.cred.password = self.statusline.prompt("Password: ", True)
            savecreds = self.statusline.prompt("Save credentials (y/N)? ")
            self.statusline.notify("Temporarily logged in. Restart soundground to log out.")
            if len(savecreds) > 0 and savecreds[0].lower() == 'y':
                self.statusline.notify("Logged in.")
                self.cred.save()
        elif cmd[0] == 'logout':
            # Remove username and password from credentials file
            self.cred.username = ''
            self.cred.password = ''
            self.cred.save()
            self.statusline.notify("Logged out.")
        elif cmd[0] == 'list':
            # Replace 'you' to actual username
            if cmd[1][:4] == "you/":
                if len(self.cred.username) < 1:
                    self.playlist.items.clear()
                    self.playlist.add("Please log in")
                    return False
                listurl = self.cred.username + cmd[1][3:]
            else:
                listurl = cmd[1]

            # Show temporary loading screen
            self.playlist.items.clear()
            self.playlist.add("Loading {}".format(listurl))

            # Fetch list and display on playlist panel
            items = self.cloudman.fetch_url(listurl)
            self.playlist.items.clear()
            if 'error' in items:
                self.playlist.add(items['error'])
                return False
            entries = items['entries']

            # Populate playlist
            self.playlist.items.clear()
            for entry in entries:
                self.playlist.add(entry['url'])

            # Start processing list
            self.cloudman.async_process_playlist()
        else:
            self.statusline.notify("Unknown command `{}`".format(cmd[0]))

        return True
