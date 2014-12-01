#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Medias locator
==============
"""

from __future__ import absolute_import

import os.path


class PathMediasLocator(object):
    """
    Returns medias relatively to the root directory *base*.
    """
    def __init__(self, base):
        self.base = base

    def __call__(self, path):
        path = path.lstrip('/')
        return os.path.join(self.base, path)


class NoMediasLocator(object):
    """
    Raises an error when a media is asked.
    """
    def __call__(self, path):
        raise RuntimeError('No media path')
