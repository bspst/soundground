#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cloud Manager
Handles communication to SoundCloud
"""

import threading
import youtube_dl

class CloudManager(object):
    base = 'https://soundcloud.com/'

    def __init__(self, cred=None, playlist=None):
        # Use empty credentials if not given
        if cred == None:
            cred = credman.Credentials()

        self.cred = cred
        self.playlist = playlist
        options = {
            'username': self.cred.username,
            'password': self.cred.password,
            'quiet': True,
        }
        self.ydl = youtube_dl.YoutubeDL(options)
        # Number of threads to use for downloading media info
        self.n_threads = 4
        self.dl_threads = [None]*self.n_threads

    def async_process_playlist(self):
        """
        Process the playlist in background
        """
        thread = threading.Thread(target=self.process_playlist)
        thread.run()
        return thread

    def process_playlist(self):
        """
        Get URL info and edit the playlist
        """
        def process_item(self, index):
            """
            Processes a single playlist item
            """
            # Display status
            self.playlist.items[index]['caption'] += ' [fetching info]'
            self.playlist.draw()

            # Fetch info
            list_items = self.playlist.items
            try:
                info = self.process_url(list_items[index]['value'])
            except Exception as ex:
                info = {'error': str(ex)}

            list_items[index]['info'] = info

            # Set item title
            if 'error' in info:
                title = info['error']
            elif 'uploader' in info:
                title = "{} - {}".format(info['uploader'], info['title'])
            else:
                username = info['webpage_url'].split('/')[3]
                title = "{} - {}".format(username, info['title'])

            list_items[index]['caption'] = title

            # Re-draw playlist
            self.playlist.draw()

        # Iterate through items
        index = 0
        while index < len(self.playlist.items)-1:
            # Find a free thread
            for i in range(self.n_threads):
                if self.dl_threads[i] == None or not self.dl_threads[i].isAlive():
                    # Create thread and run
                    self.dl_threads[i] = threading.Thread(target=process_item, args=(self, index))
                    self.dl_threads[i].start()
                    index += 1
                    if index == len(self.playlist.items):
                        break

    def process_url(self, url):
        """
        Gets info on a URL
        """
        with self.ydl as ydl:
            try:
                # Add base domain if the URL doesn't have it
                if url[:8] != 'https://':
                    url = self.base + url

                return ydl.extract_info(url, download=False)
            except Exception as ex:
                return {'error': str(ex)}

    def fetch_url(self, url):
        """
        Fetches items in a SoundCloud list
        """
        with self.ydl as ydl:
            try:
                if url[:8] != 'https://':
                    url = self.base + url

                return ydl.extract_info(url, download=False, process=False)
            except Exception as ex:
                return {'error': str(ex)}
