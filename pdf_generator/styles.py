#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import absolute_import

import six
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


class Paragraph(BaseParagraph):
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
    def __init__(self, text, style=snormal, bulletText=None, frags=None, caseSensitive=1, encoding='utf8', **kw):
        if isinstance(style, six.string_types):
            style = styles[style]

        if kw:
            style = ParagraphStyle('style', parent=style, **kw)

        BaseParagraph.__init__(self, text, style, bulletText=bulletText, frags=frags,
                               caseSensitive=caseSensitive, encoding=encoding)

    def __eq__(self, other):
        return (isinstance(other, BaseParagraph) and
                self.text == other.text and self._same_style(other))

    def _same_style(self, other):
        if self.style is other.style:
            return True

        style, other = self.style.__dict__, other.style.__dict__
        return all(style[k] == other[k]
                   for k in style if k != 'name' and k != 'parent')

    def __repr__(self):
        return 'P({})'.format(self.text[:40].encode('ascii', 'ignore'))

    def __bool__(self):
        return bool(self.text.strip())

    __nonzero__ = __bool__


class RotatedParagraph(Paragraph):
    def __init__(self, *args, **kw):
        self.rotation = kw.pop('rotation')
        Paragraph.__init__(self, *args, **kw)

    def minWidth(self):
        return BaseParagraph.minWidth(self) * self.rotation.cos()

    def draw(self):
        self.width -= self.height * self.rotation.sin()
        self.canv.translate(self.height * self.rotation.sin(), 0)
        self.canv.rotate(self.rotation)
        Paragraph.draw(self)

    def wrap(self, avail_width, avail_height):
        cos = self.rotation.cos()
        sin = self.rotation.sin()
        avail_width = cos * avail_width + sin * avail_height
        avail_height = cos * avail_height + sin * avail_width
        return Paragraph.wrap(self, avail_width, avail_height)


def bold(string, *args, **kw):
    """
    Return string as a :class:`Paragraph` in bold
    """
    cls = RotatedParagraph if kw.get('rotation') else Paragraph
    return cls(u'<b>{}</b>'.format(string), *args, **kw)


def italic(string, *args, **kw):
    """
    Return string as a :class:`Paragraph` in italic
    """
    cls = RotatedParagraph if kw.get('rotation') else Paragraph
    return cls(u'<i>{}</i>'.format(string), *args, **kw)


def HSpacer(width):
    """
    A horizontal spacer of given *width*
    """
    return Spacer(0, width)


def Image(path, width=None, height=None, ratio=None, hAlign='CENTER', **kw):
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

    image = BaseImage(path, width, height, **kw)
    image.hAlign = hAlign
    return image
