#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import collections

from reportlab.platypus import (
    PageBreak,
    FrameBreak,
    NextPageTemplate,
)


class Story(collections.MutableSequence):
    def __init__(self, template):
        self._template = template
        self._story = list()
        self._index = 0

    @property
    def template(self):
        return self._template

    def next_page(self):
        self._story.append(PageBreak())

    def next_frame(self):
        self._story.append(FrameBreak())

    def next_template(self, name=None):
        if name is None:
            name = self._index = (self._index + 1) % len(self._template.page_templates)
        self._story.append(NextPageTemplate(name))

    def __len__(self):
        return len(self._story)

    def __iter__(self):
        return iter(self._story)

    def __getitem__(self, index):
        return self._story[index]

    def insert(self, index, value):
        return self._story.insert(index, value)

    def __setitem__(self, index, value):
        self._story[index] = value

    def __delitem__(self, index):
        del self._story[index]

    def build(self, out, title, author, debug=False, **kw):
        doc = self._template(out, title, author, debug)
        doc.build(self._story, **kw)
        return out
