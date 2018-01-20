#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auxilary functions
"""

from datetime import datetime

def format_millis(millis):
    """
    Formats milliseconds to a mm:ss format
    """
    return datetime.fromtimestamp(millis/1000.0).strftime("%M:%S")

def debug(msg):
    f = open('~/.soundground/debug.log', 'a')
    f.write(str(msg))
    f.write("\n")
    f.close()
