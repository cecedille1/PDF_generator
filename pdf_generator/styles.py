#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from reportlab.platypus import (
    Paragraph as BaseParagraph,
    Image as BaseImage,
    Spacer,
)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet


styles = getSampleStyleSheet()
snormal = ParagraphStyle('normal')


def Paragraph(text, style=snormal, **kw):
    if isinstance(style, basestring):
        style = styles[style]

    if kw:
        style = ParagraphStyle('style', parent=style, **kw)
    return BaseParagraph(text, style)


def bold(string, *args, **kw):
    """
    Return string as a :class:`Paragraph` in bold
    """
    return Paragraph(u'<b>{}</b>'.format(string), *args, **kw)


def italic(string, *args, **kw):
    """
    Return string as a :class:`Paragraph` in italic
    """
    return Paragraph(u'<i>{}</i>'.format(string), *args, **kw)


def HSpacer(width):
    return Spacer(0, width)


def Image(path, width=None, height=None, ratio=None):
    if width and ratio:
        height = width / ratio
    elif height and ratio:
        width = height * ratio

    return BaseImage(path, width, height)
