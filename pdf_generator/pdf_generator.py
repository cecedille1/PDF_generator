#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PDF Builder
===========

The :class:`Story` is the base class of the pdf generator. Each story is a list
of flowables with a page template. The method :meth:`Story.build` generates a
PDF file in the given output by applying the flowables on the template.
"""

from __future__ import absolute_import

import six
import collections

from reportlab.platypus import (
    PageBreak,
    FrameBreak,
    NextPageTemplate,
)
from pdf_generator.styles import Paragraph

__all__ = [
    'Story',
]


class Story(collections.MutableSequence):
    """
    A list of flowables.

    The template is a :class:`~pdf_generator.templates.Template` or a derived
    class.
    """
    def __init__(self, template):
        self._template = template
        self._story = list()
        self._index = 0

    @property
    def template(self):
        return self._template

    def append(self, flowable):
        """
        Add *flowable* to the story.
        """
        if isinstance(flowable, six.string_types):
            flowable = Paragraph(flowable)
        super(Story, self).append(flowable)

    def next_page(self):
        """
        Add a :class:`reportlab.platypus.PageBreak` to skip to the next page
        """
        self._story.append(PageBreak())

    def next_frame(self):
        """
        Add a :class:`reportlab.platypus.FrameBreak` to skip to the next frame
        of the template
        """
        self._story.append(FrameBreak())

    def next_template(self, name=None):
        """
        Add a :class:`reportlab.platypus.NextPageTemplate` to skip to the next
        template page of the template. If *name* is specified, the template is
        selected by its name, else the next page of the template is selected.
        """
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

    def build(self, out, title, author, debug=False,
              header=None, footer=None, page_end=None, **kw):
        """
        Renders the template in out.

        Out is a file-like object to write the template. The title and author
        are set as meta datas on the generated template. If *debug* is True,
        the outlines of the frames are printed in the PDF.
        """
        doc = self._template(out, title, author, debug,
                             header=header, footer=footer, page_end=page_end)
        doc.build(self._story, **kw)
        return out
