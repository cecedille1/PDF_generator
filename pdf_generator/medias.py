#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os.path


class PathMediasLocator(object):
    def __init__(self, base):
        self.base = base

    def __call__(self, path):
        path = path.lstrip('/')
        return os.path.join(self.base, path)


class NoMediasLocator(object):
    def __call__(self, path):
        raise RuntimeError('No media path')
