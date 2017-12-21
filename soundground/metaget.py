#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MetaGet
Fetches playlist contents and track data
"""

import youtube_dl

class ListFetcher(object):
    """
    Fetches playlist contents
    """
    def __init__(self, cred=None):
        # Check credentials
        self.cred = cred
        if cred == None:
            from soundground import credman
            self.cred = credman.Credentials()
            self.cred.load()

    def fetch(self, url):
        # Get contents of Soundcloud list
        opts = {
            'username': self.cred.username,
            'password': self.cred.password,
            'simulate': True,
            'forcejson': True
        }
        with youtube_dl.YoutubeDL(opts) as ydl:
            raise Exception(ydl.download([url]))
