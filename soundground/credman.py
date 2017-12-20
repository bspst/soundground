#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Credentials Manager
Sacves and loads SoundCloud username/password combos
"""

import os, json

class Credentials(object):
    def __init__(self):
        self.username = ''
        self.password = ''
        self.base_dir = os.path.expanduser("~/.soundground/")
        self.save_name = "credentials.json"
        self.save_location = os.path.join(self.base_dir, self.save_name)

    def save(self):
        """
        Save credentials to a file
        """
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

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
        try:
            with open(self.save_location, 'r') as credfile:
                creds = json.loads(credfile.read())
                self.username = creds['u']
                self.password = creds['p']
                return True
        except:
            return False
