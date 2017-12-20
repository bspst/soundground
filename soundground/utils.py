#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auxilary functions
"""

from datetime import datetime

def format_millis(millis):
    return datetime.fromtimestamp(millis/1000.0).strftime("%M:%S")
