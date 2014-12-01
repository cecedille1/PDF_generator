#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import absolute_import

from reportlab.platypus import (
    Paragraph as BaseParagraph,
    Image as BaseImage,
    Spacer,
)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

__all__ = [
    'Paragraph',
    'HSpacer',
    'Image',
    'bold',
    'italic',
]


styles = getSampleStyleSheet()
snormal = ParagraphStyle('normal')


def Paragraph(text, style=snormal, **kw):
    """
    A :class:`reportlab.platypus.Paragraph` shortcut.

    *style* is either the name of a sample style or a :class:`ParagraphStyle`
    instance.

    To create a paragraph with default style.

    >>> Paragraph(text)

    To create a paragraph with some style, pass it as keyword

    >>> Paragraph(text, fontSize=14)

    To create a paragraph with an existing :class:`ParagraphStyle`

    >>> style = ParagraphStyle('important', color=colors.red)
    >>> Paragraph(text, style)

    To create a paragraph with an existing style and additional rules

    >>> style = ParagraphStyle('important', color=colors.red)
    >>> Paragraph(text, style, fontSize=20)

    To create a paragraph with an style from the sample stylesheet

    >>> Paragraph(text, 'h2')

    To create a paragraph with an style from the sample stylesheet and additional rules

    >>> Paragraph(text, 'h2', color=colors.red)
    """
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
    """
    A horizontal spacer of given *width*
    """
    return Spacer(0, width)


def Image(path, width=None, height=None, ratio=None):
    """
    An image with the file at *path*.

    The ratio is the width divided by the height of the source image. If the
    width or the height is given with the ratio, the other dimension is
    calculated from the first.
    """
    if width and ratio:
        height = width / ratio
    elif height and ratio:
        width = height * ratio

    return BaseImage(path, width, height)
