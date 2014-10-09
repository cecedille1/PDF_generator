#!/usr/bin/env python
# -*- coding: utf-8 -*-

from reportlab.pdfgen.canvas import Canvas


class NumberedCanvasFactory(object):
    def __init__(self, x, y, text):
        self._x = x
        self._y = y
        self._text = text

    def __call__(self, *args, **kw):
        return NumberedCanvas(*args,
                              x=self._x,
                              y=self._y,
                              text=self._text,
                              **kw)


class NumberedCanvas(Canvas):
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
                self._nc_text.format(self._pageNumber, len(self._codes)),
            )
            Canvas.showPage(self)

        Canvas.save(self)
