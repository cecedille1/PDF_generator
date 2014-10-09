#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from reportlab.platypus import (
    Paragraph as BaseParagraph,
)
from reportlab.lib.styles import ParagraphStyle


snormal = ParagraphStyle('normal')


def Paragraph(text, style=snormal, **kw):
    if kw:
        style = ParagraphStyle('style', **kw)
    return BaseParagraph(text, style)
