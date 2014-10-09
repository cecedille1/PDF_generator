#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import collections

from reportlab.platypus import Table, LongTable, TableStyle
from pdf_generator.styles import Paragraph


def make_para_row(texts):
    return map(Paragraph, texts)


def make_para_array(rows):
    return map(make_para_row, rows)


class TableGenerator(collections.MutableSequence):

    def __init__(self, size=None):
        self.size = size
        self.content = list()

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

    def __getattr__(self, name):
        return CellsStyle(name, self.known_styles.get(name.lower()))


class CellsStyle(object):
    def __init__(self, name, argc):
        self.name = name.upper()
        self.argc = argc

    def __call__(self, *args):
        if self.argc is not None and len(args) != self.argc:
            raise TypeError('{2}: Expecting {0} arguments, got {1}'.format(
                self.argc, len(args), self.name))
        return (self.name, ) + args


styles = Styles()
