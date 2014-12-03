#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mock
import unittest

from reportlab.platypus import (
    Table,
    FrameBreak,
)
from pdf_generator import Paragraph

from pdf_generator.pdf_generator import (
    Story,
)


class TestStory(unittest.TestCase):
    def setUp(self):
        self.template = mock.Mock()
        self.story = Story(self.template)

    def test_append_string(self):
        self.story.append('String')
        self.assertEqual(list(self.story), [Paragraph('String')])

    def test_append(self):
        table = Table([['A']])
        self.story.append(table)
        self.assertEqual(list(self.story), [table])

    def test_build(self):
        p1 = Paragraph('P1')
        self.story.append(p1)

        out = mock.Mock()
        self.story.build(out, 'title', 'author')
        self.template.assert_called_once_with(out, 'title', 'author', False)
        self.template.return_value.build.assert_called_once_with([p1])
