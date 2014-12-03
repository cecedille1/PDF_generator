#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from pdf_generator.medias import PathMediasLocator


class TestPML(unittest.TestCase):
    def setUp(self):
        self.pml = PathMediasLocator('/path/to/base')

    def test_locate_absolute(self):
        self.assertEqual(self.pml('/path/resource'), '/path/to/base/path/resource')

    def test_locate_relative(self):
        self.assertEqual(self.pml('path/resource'), '/path/to/base/path/resource')
