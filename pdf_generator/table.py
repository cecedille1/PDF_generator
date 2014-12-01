#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import collections

from reportlab.lib import colors
from reportlab.platypus import (
    Table,
    LongTable,
    TableStyle,
    Paragraph as ParagraphClass
)




class TableGenerator(collections.MutableSequence):

    def __init__(self, size=None):
        self._size = size
        self.content = list()

    @property
    def size(self):
        if self._size:
            return self._size
        return max(len(x) for x in self)

    def __len__(self):
        return len(self.content)

    def __iter__(self):
        return len(self.content)

    def __setitem__(self, index, value):
        self.content[index] = value

    def __getitem__(self, index):
        return self.content[index]

    def __delitem__(self, index):
        del self.content[index]

    def insert(self, index, value):
        self.content.insert(index, value)

    def add_a_line(self):
        self.append([''] * self.size)

    def add_row(self, row):
        self.append(make_para_row(row))

    def add_array(self, array):
        self.extend(make_para_array(array))

    def add_header_row(self, row):
        self.add_row(map(lambda x: '<b>%s</b>' % x, row))

    def get_table(self, *style, **kw):
        return Table(self.content, style=TableStyle(style), **kw)

    def get_long_table(self, *style, **kw):
        return LongTable(self.content, style=TableStyle(style), **kw)


class Styles(object):
    known_styles = {
        # borders
        'grid': 4,
        'box': 4,
        'linebelow': 4,
        'lineafter': 4,

        'background': 3,
        'valign': 3,
    }

    def __init__(self, *args):
        self.args = args

    def __getattr__(self, name):
        return CellsStyle(name, self.known_styles.get(name.lower()), self.args)


class CellsStyle(object):
    def __init__(self, name, argc, args):
        self.name = name.upper()
        self.argc = argc
        self.args = args

    def __call__(self, *args):
        args = self.args + args

        if self.argc is not None and len(args) != self.argc:
            raise TypeError('{2}: Expecting {0} arguments, got {1}'.format(
                self.argc, len(args), self.name))
        return (self.name, ) + args


styles = Styles()

styles.all = Styles((0, 0), (-1, -1))

styles.first_row = Styles((0, 0), (-1, 0))
styles.first_rows = lambda x: Styles((0, 0), (-1, x))

styles.last_row = Styles((0, -1), (-1, -1))
styles.last_rows = lambda x: Styles((0, -x), (-1, -1))

styles.first_col = Styles((0, 0), (0, -1))
styles.first_cols = lambda x: Styles((0, 0), (x, -1))

styles.last_col = Styles((-1, 0), (-1, -1))
styles.last_cols = lambda x: Styles((-x, 0), (-1, -1))

styles.grid = styles.all.Grid(1, colors.black)
