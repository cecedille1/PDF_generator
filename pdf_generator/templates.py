#!/usr/bin/env python
# -*- coding: utf-8 -*-

from reportlab.platypus import (
    Frame,
    BaseDocTemplate,
    PageTemplate,
    SimpleDocTemplate,
)
from reportlab.lib import pagesizes


class Fraction(object):
    def __init__(self, ratio):
        self._ratio = ratio

    def __mul__(self, x):
        return x * self._ratio

    def __add__(self, x):
        if x == 0:
            return self
        if not isinstance(x, Fraction):
            raise ValueError('Can only add a fraction to a fraction')
        return Fraction(x._ratio + self._ratio)

    def __repr__(self):
        if self._ratio == 0:
            return '0/0'
        for x in xrange(2, 20):
            if self._ratio * x % 1 == 0.0:
                return '{0} / {1}'.format(int(self._ratio * x), x)
        return str(self._ratio)


class BaseTemplate(object):
    def __init__(self, pagesize=None, margins=None):
        self.width, self.height = pagesize or pagesizes.A4
        margins = margins or (36, 36, 18)
        self._mtop, self._mright, self._mbottom, self._mleft = self.explode(margins)

    def explode(self, margins):
        """
        Explode a value or a tuple in 4 values as CSS borders, paddings and
        margins
        """
        if not isinstance(margins, (tuple, list)):
            margins = [margins]

        if len(margins) == 1:
            mleft = mright = mtop = mbottom = margins[0]
        elif len(margins) == 2:
            mbottom, mright = margins
            mleft = mright
            mtop = mbottom
        elif len(margins) == 3:
            mtop, mright, mbottom = margins
            mleft = mright
        elif len(margins) == 4:
            mtop, mright, mbottom, mleft = margins[0]
        else:
            raise ValueError('Bad values for margins')
        return mtop, mright, mbottom, mleft

    @property
    def printable_width(self):
        return self.width - self._mleft - self._mright

    @property
    def printable_height(self):
        return self.height - self._mtop - self._mbottom

    @property
    def pagesize(self):
        return (self.width, self.height)

    def __call__(self, out, title, author):
        raise NotImplementedError('This method should return a DocTemplate')


class SimpleTemplate(BaseTemplate):
    def __call__(self, out, title, author, debug=False):
        return SimpleDocTemplate(out, pagesize=self.pagesize,
                                 rightMargin=self._mright,
                                 leftMargin=self._mleft,
                                 topMargin=self._mtop,
                                 bottomMargin=self._mbottom,
                                 author=author,
                                 title=title,
                                 showBoundary=debug,
                                 )


class TemplateRows(object):
    def __init__(self):
        self._rows = []
        self._current_height = 0

    def row(self, height=None):
        if self._current_height is None:
            raise ValueError('No space remaining')

        row = TemplateRow(self._current_height, height)
        if height is None:
            self._current_height = height
        else:
            self._current_height = height + self._current_height

        self._rows.append(row)
        return row

    def __iter__(self):
        for row in self._rows:
            for cell in row:
                yield cell


class TemplateRow(object):
    def __init__(self, y, height):
        self.y = y
        self.height = height
        self._cells = []
        self._consumed = 0

    def __iter__(self):
        for x, width in self._cells:
            yield x, self.y, width, self.height

    def skip(self, width):
        self._consumed = width + self._consumed
        return self

    def cell(self, width=None):
        if self._consumed is None:
            raise ValueError('No space left')

        self._cells.append((self._consumed, width))
        if width is None:
            self._consumed = None
        else:
            self._consumed = width + self._consumed
        return self

    def split(self, x, *args):
        """
        split(x)

        Split the row in *x* equal parts

        split(x, y, z, ...)

        Split the row in as many parts as arguments, weighed by each value.
        Ex split(2, 3, 2, 1) creates 1/3, 1/2, 1/3, 1/6.
        """
        if self._cells:
            raise ValueError('Cannot split already divided cell')

        if not args:
            args = [1] * x
        else:
            args = (x, ) + args

        total = float(sum(args))
        fractions = [Fraction(y/total) for y in args]

        acc = Fraction(0)
        for fraction in fractions:
            self._cells.append((acc, fraction))
            acc += fraction


class Template(BaseTemplate):
    def __init__(self, pagesize=None, margins=None, pageEnd=None):
        super(Template, self).__init__(pagesize, margins)
        self.page_templates = []

        self.pageEnd = pageEnd
        self.left = self._mleft
        self.right = self.width - self._mright
        self.top = self.height - self._mtop
        self.bottom = self._mbottom

    def _resolve_dim(self, dim, ref):
        if dim is None:
            return ref
        elif isinstance(dim, Fraction):
            return dim * ref
        elif isinstance(dim, (int, float)):
            return dim

        raise ValueError()

    def get_frame(self, x, y, width=None, height=None, padding=None):
        # Invert the coordinates, from bottom left to top left

        width = self._resolve_dim(width, self.width)
        height = self._resolve_dim(height, self.height)

        x = self._resolve_dim(x, self.width)
        y = self.height - self._resolve_dim(y, self.height) - height

        if x < self.left:
            width -= self.left - x
            x = self.left
        if x + width > self.right:
            width = self.right - x

        if y < self.bottom:
            height -= self.bottom - y
            y = self.bottom

        if y + height > self.top:
            height = self.top - y

        ptop, pright, pbottom, pleft = self.explode(padding if padding is not None else 6)
        return Frame(x, y, width, height,
                     leftPadding=pleft,
                     topPadding=ptop,
                     bottomPadding=pbottom,
                     rightPadding=pright,
                     )

    def add_page(self, id, frame_defs=None, padding=None):
        if frame_defs is None:
            frame_defs, id = id, None

        id = id or '_page-{0}'.format(len(self.page_templates))

        frames = [self.get_frame(*frame_def, padding=padding) for frame_def in frame_defs]
        pt = PageTemplate(id, frames)
        if self.pageEnd is not None:
            pt.onPageEnd = self.pageEnd

        self.page_templates.append(pt)
        return pt

    def add_whole_page(self, id=None, padding=None):
        self.add_page(id, [(0, 0)], padding)

    def __call__(self, out, title, author, debug=False):
        return BaseDocTemplate(
            out,
            pagesize=self.pagesize,
            pageTemplates=self.page_templates,
            title=title,
            author=author,
            rightMargin=self._mright,
            leftMargin=self._mleft,
            topMargin=self._mtop,
            bottomMargin=self._mbottom,
            showBoundary=debug,
        )
