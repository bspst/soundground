#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cloud Manager
Handles communication to SoundCloud
"""

import youtube_dl

class CloudManager(object):
    base = 'https://soundcloud.com/'

    def __init__(self, cred=None):
        # Use empty credentials if not given
        if cred == None:
            cred = credman.Credentials()

        self.cred = cred

    def fetch_list(self, url):
        """
        Fetches items in a SoundCloud list
        """
        options = {
            'username': self.cred.username,
            'password': self.cred.password,
            'quiet': True,
        }
        with youtube_dl.YoutubeDL(options) as ydl:
            try:
                return ydl.extract_info(self.base + url, download=False, process=False)
            except Exception as ex:
                return {'error': str(ex.exc_info[1])}
