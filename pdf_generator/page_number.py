#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Page numbers
============

The :class:`NumberedCanvasFactory` provides a way to print page numbers on
PDF templates. It's used as the canvasmaker argument of :class:`Story.build`.

This examples prints the page number as "1/2" and "2/2" in the top right corner:

>>> story = Story(SimpleTemplate())
>>> story.append(two_pages_of_text)
>>> story.build(out,
...                  title=u'PDF with page number',
...                  author=u'Enix PDF Generator',
...                  canvasmaker=NumberedCanvasFactory(-1 * units.cm, 1.5 * units.cm, '{0}/{1}'),
...                  )

"""

import six
from reportlab.pdfgen.canvas import Canvas


__all__ = [
    'NumberedCanvasFactory',
]


class NumberedCanvasFactory(object):
    """
    A generator of :class:`NumberedCanvas`.

    It takes a *x* and a *y*, being the coordinate of the page number on the
    page. The x and y are relative to the top left corner of the page.
    Negative dimensions are relative to the bottom right corner of the page.

    *text* is the pattern used for representing the page number. The format
    provides 2 values, 0: the current page number and 1 the total number of
    pages.
    """

    def __init__(self, x, y, text='{0}/{1}'):
        self._x = x
        self._y = y
        if callable(text):
            self._text = text
        elif isinstance(text, six.string_types):
            self._text = text.format
        else:
            raise TypeError('Unexpected value for text: {!r}'.format(text))

    def __call__(self, *args, **kw):
        return NumberedCanvas(*args,
                              x=self._x,
                              y=self._y,
                              text=self._text,
                              **kw)


class NumberedCanvas(Canvas):
    """
    :class:`reportlab.pdfgen.canvas.Canvas` subclass supporting page numbers.
    """
    def __init__(self, *args, **kwargs):
        self._nc_x = kwargs.pop('x')
        self._nc_y = kwargs.pop('y')
        self._nc_text = kwargs.pop('text')

        Canvas.__init__(self, *args, **kwargs)
        self._codes = []

    def showPage(self):
        self._codes.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        x, y = self._nc_x, self._nc_y

        if x < 0:
            x = self._pagesize[0] + x

        if y > 0:
            y = self._pagesize[1] - y
        else:
            y = - y

        for code in self._codes:
            # recall saved page
            self.__dict__.update(code)
            self.setFont('Helvetica', 7)
            self.drawRightString(
                x, y,
                self._nc_text(self._pageNumber, len(self._codes)),
            )
            Canvas.showPage(self)

        Canvas.save(self)
