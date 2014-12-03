#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Medias locator
==============

Medias locator returns a path on the file system from the *src* of an img tag.

.. data:: PLACEHOLDER

    A special object that indicates to the renderer to use a placeholder
    instead of a media.
"""

from __future__ import absolute_import

import os.path


PLACEHOLDER = object()


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


class DebugMediasLocator(object):
    """
    Return :data:`PLACEHOLDER`
    """

    def __call__(self, path):
        return PLACEHOLDER
