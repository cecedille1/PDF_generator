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

from StringIO import StringIO
from HTMLParser import HTMLParser
from collections import deque

from reportlab.platypus import Image, Table
from reportlab.lib import enums

from pdf_generator.medias import NoMediasLocator
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

    if isinstance(link_handler, basestring):
        link_handler = PrefixLinkHandler(link_handler)

    parser = Parser(media_locator or NoMediasLocator(), link_handler)
    parser.feed(text)
    return parser.get_result()

# pop, call fn and add result


class PrefixLinkHandler(object):
    def __init__(self, prefix):
        self.prefix = prefix.rstrip('/')

    def __call__(self, url):
        if not url.startswith('/'):
            url = '/' + url
        return self.prefix + url


def end_block(fn):
    def cb(self):
        self.new_para()
        item = fn(self.stack.pop())
        self.stack[-1].append(item)
    return cb


class Parser(HTMLParser):

    def on_img(self, attrs):
        attr = dict(attrs)
        width = None
        if 'width' in attrs:
            width = int(attrs['width']) / 10
        height = None
        if 'height' in attrs:
            height = int(attrs['height']) / 10

        self.new_para()
        self.stack[-1].append(
            Image(self.media_locator(attr['src']), height=height, width=width))

    @end_block
    def block_end(item):
        # map to make a column and not a row
        return Table(map(lambda x: [x], item))

    @end_block
    def on_center_end(item):
        return Table(map(lambda x: [x], item), hAlign=enums.TA_CENTER)

    def on_li_end(self):
        para = self.clean_buffer()
        para.bulletText = '-'
        self.stack[-1].append(para)

    def on_a_start(self, attrs):
        attr = dict(attrs)
        href = attr['href']
        if self.link_handler:
            href = self.link_handler(href)
        self.add_buffer(u'<link href="{0}">'.format(href))

    def on_a_end(self):
        self.add_buffer('</link>')

    def block_start(self, x=None):
        self.new_para()
        self.stack.append([])

    def ignore(self, x=None):
        pass

    def add_br(self, attr):
        self.add_buffer('<br />')

    handlers_start = {
        'a': on_a_start,
        'center': block_start,
        'blockquote': block_start,
        'ul': block_start,
        'li': ignore,
        'br': add_br,
        'img': on_img
    }
    handlers_end = {
        'a': on_a_end,
        'center': on_center_end,
        'blockquote': block_end,
        'ul': block_end,
        'li': on_li_end
    }
    handlers_startend = {
        'img': on_img,
    }

    def __init__(self, media_locator, link_handler):
        HTMLParser.__init__(self)
        self.media_locator = media_locator
        self.link_handler = link_handler
        self.new_buffer()
        self.stack = deque()
        self.stack.append([])

    def handle_starttag(self, tag, attrs):
        if tag in self.handlers_start:
            self.handlers_start[tag](self, attrs)
        else:
            self.add_buffer(self.get_starttag_text())

    def handle_startendtag(self, tag, attrs):
        if tag in self.handlers_startend:
            self.handlers_startend[tag](self, attrs)
        else:
            self.add_buffer(self.get_starttag_text())

    def handle_endtag(self, tag):
        if tag in self.handlers_end:
            self.handlers_end[tag](self)
        else:
            self.add_buffer('</%s>' % tag)

    def handle_data(self, data):
        self.add_buffer(data)

    def new_para(self):
        p = self.clean_buffer()
        if p is not None:
            self.stack[-1].append(p)

    def add_buffer(self, text):
        self.buff_clean = False
        self.buff.write(text)

    def clean_buffer(self):
        if not self.buff_clean:
            text = self.buff.getvalue()
            self.buff.close()
            self.new_buffer()
            return Paragraph(text)
        return None

    def new_buffer(self):
        self.buff_clean = True
        self.buff = StringIO()

    def get_result(self):
        # empty last buffer
        self.new_para()
        if len(self.stack) == 1:
            return self.stack.pop()
        return Table(self.stack)
