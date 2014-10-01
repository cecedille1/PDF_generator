#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path


class ImagePathLocator(object):
    def __init__(self, base):
        self.base = base

    def __call__(self, path):
        return os.path.join(self.base, path)


class NoImageLocator(object):
    def __call__(self, path):
        raise RuntimeError()
