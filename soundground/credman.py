#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Credentials Manager
Sacves and loads SoundCloud username/password combos
"""

import json

class Credentials(object):
    def __init__(self):
        self.username = None
        self.password = None
        self.save_location = "~/.soundground/credentials.json"

    def save(self):
        """
        Save credentials to a file
        """
        with open(self.save_location, 'w') as credfile:
            contents = json.dumps({
                'u': self.username,
                'p': self.password
            })
            credfile.write(contents)

    def load(self):
        """
        Load credentials from file
        """
        with open(self.save_location, 'r') as credfile:
            creds = json.loads(credfile.read())
            self.username = creds['u']
            self.password = creds['p']
