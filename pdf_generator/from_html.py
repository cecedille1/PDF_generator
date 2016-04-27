#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HTML
====

Transforms HTML in PDF templates.

>>> html_to_rlab('<h1>Title</h1><p><img src="lion.png" /></p>',
...              PathMediasLocator('/var/www/medias'))


The supported tags are: h1-h6, p, center, blockquote, a, br, ul, li
"""

from __future__ import absolute_import

import six

from io import StringIO
from six.moves.html_parser import HTMLParser
from collections import deque

from reportlab.platypus import (
    Image,
    Table,
    XBox,
    TableStyle,
)
from reportlab.lib import enums
from reportlab.lib.styles import ParagraphStyle

from pdf_generator.medias import NoMediasLocator, PLACEHOLDER
from pdf_generator.styles import Paragraph

__all__ = [
    'html_to_rlab'
]


def html_to_rlab(text, media_locator=None, link_handler=None):
    """
    Transforms text from html string to a list of flowables.

    The medias (from the img tags) are located by the media_locator. By default
    an instance of :class:`pdf_generator.medias.NoMediasLocator` is used that
    raises if a media is required.

    The url (from the a tags) of the links are transformed by the *link_handler*.
    The *link_handler* can be a callable, then its called with the raw href of
    the a tag and must return the url to use in the link. The *link_handler*
    can also be a string, and then is used as a prefix for the links.

    Examples:

    >>> html_to_rlab('<a href="/index.html">Index</a>', link_handler='http://example.com')
    Paragraph('<link href="http://example.com/index.html">Index</link>')
    """

    if isinstance(link_handler, six.string_types):
        link_handler = PrefixLinkHandler(link_handler)

    parser = Parser(media_locator or NoMediasLocator(), link_handler)
    parser.feed(text)
    content = [[x] for x in parser.get_result()]
    return Table(content)

# pop, call fn and add result


class PrefixLinkHandler(object):
    def __init__(self, prefix):
        self.prefix = prefix.rstrip(u'/')

    def __call__(self, url):
        if not url.startswith(u'/'):
            url = u'/' + url
        return self.prefix + url


class Rules(object):
    def __getitem__(self, item):
        return getattr(self, item)

    def __contains__(self, value):
        return hasattr(self, value)


class StartEndRules(Rules):
    def __init__(self, media_locator, link_handler):
        self.media_locator = media_locator
        self.link_handler = link_handler

    def img(self, tag, attrs):
        attrs = dict(attrs)

        width = None
        if 'width' in attrs:
            width = int(attrs['width'])

        height = None
        if 'height' in attrs:
            height = int(attrs['height'])

        src = self.media_locator(attrs['src'])
        if src is PLACEHOLDER:
            return XBox(height=height or 40, width=width or 40, text=attrs['src'])

        return Image(src, height=height, width=width)

    def br(self, tag, attrs):
        return u'<br />'


class StartRules(StartEndRules):
    def next(self, tag, attrs):
        return None

    p = ul = li = blockquote = center = h1 = h2 = h3 = h4 = h5 = h6 = next

    def a(self, tag, attrs):
        attr = dict(attrs)
        href = attr['href']

        if self.link_handler:
            href = self.link_handler(href)

        return u'<link href="{0}">'.format(href)

    def strong(self, tag, attr):
        return u'<b>'

    def em(self, tag, attr):
        return u'<i>'


class EndRules(Rules):
    def a(self, tag, value, stack):
        return u'</link>'

    def h6(self, tag, value, stack):
        return Paragraph(value, tag)

    h1 = h2 = h3 = h4 = h5 = h6

    def _center(self, values):
        for x in values:
            if isinstance(x, Paragraph):
                x.style = ParagraphStyle('center', parent=x.style, alignment=enums.TA_CENTER)
            elif isinstance(x, Image):
                x.hAlign = 'CENTER'
            elif isinstance(x, list):
                self._center(x)
        return values

    def center(self, tag, value, stack):
        if value.strip():
            stack.append(Paragraph(value))
        return Table([[x] for x in self._center(stack)],
                     style=TableStyle([('ALIGNMENT', (0, 0), (-1, -1), 'CENTER')]))

    def stacked(self, tag, value, stack):
        if value.strip():
            stack.append(Paragraph(value))
        return stack

    ul = blockquote = stacked

    def li(self, tag, value, stack):
        if value:
            return Paragraph(value, bulletText='-')

    def p(self, tag, value, stack):
        if value.strip():
            return Paragraph(value)

    def strong(self, tag, value, stack):
        return u'</b>'

    def em(self, tag, value, stack):
        return u'</i>'


class Parser(HTMLParser):
    def __init__(self, media_locator, link_handler):
        HTMLParser.__init__(self)
        self.handlers_start = StartRules(media_locator, link_handler)
        self.handlers_startend = StartEndRules(media_locator, link_handler)
        self.handlers_end = EndRules()

        self.new_buffer()
        self.stack = deque()
        self.stack.append([])

    def handle_starttag(self, tag, attrs):
        if tag in self.handlers_start:
            value = self.handlers_start[tag](tag, attrs)
            if isinstance(value, six.string_types):
                self.add_buffer(value)
            elif value is None:
                self.push_buffer()
                self.stack.append([])
            else:
                self.push_buffer()
                self.stack.append(value)
        else:
            self.add_buffer(self.get_starttag_text())

    def handle_startendtag(self, tag, attrs):
        if tag in self.handlers_startend:
            value = self.handlers_startend[tag](tag, attrs)
            if isinstance(value, six.string_types):
                self.add_buffer(value)
            elif value is None:
                self.stack[-1].append(self.clean_buffer())
            else:
                self.push_buffer()
                self.stack[-1].append(value)
        else:
            self.add_buffer(self.get_starttag_text())

    def handle_endtag(self, tag):
        if tag in self.handlers_end:
            stack = self.stack.pop()
            buffer = self.clean_buffer()
            value = self.handlers_end[tag](tag, buffer, stack)

            if isinstance(value, six.string_types):
                self.add_buffer(buffer)
                self.add_buffer(value)
                self.stack.append(stack)
            elif isinstance(value, Paragraph) or value is None:
                if len(stack) == 1 and not value:
                    self.stack[-1].append(stack[0])
                elif not stack and value:
                    self.stack[-1].append(value)
                elif value:
                    stack.append(value)
                    self.stack.append(stack)
            else:
                self.stack[-1].append(value)

        else:
            self.add_buffer(u'</%s>' % tag)

    def handle_data(self, data):
        self.add_buffer(data)

    def add_buffer(self, text):
        self.buff_clean = False
        self.buff.write(text)

    def push_buffer(self):
        content = self.clean_buffer()
        if content.strip():
            self.stack[-1].append(Paragraph(content))

    def clean_buffer(self, *args, **kw):
        if self.buff_clean:
            return ''

        text = self.buff.getvalue()
        self.new_buffer()
        return text

    def new_buffer(self):
        self.buff_clean = True
        self.buff = StringIO()

    def get_result(self):
        # empty last buffer
        self.push_buffer()
        return self.stack.pop()
