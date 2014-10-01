#!/usr/bin/env python
# -*- coding: utf-8 -*-

from reportlab.platypus import Table, LongTable

from pdf_generator.styles import make_para_row, make_para_array


class TableGenerator(list):

    def __init__(self, size=None):
        self.size = size
        super(TableGenerator, self).__init__()

    def add_a_line(self):
        self.append([''] * self.size)

    def add_row(self, row):
        self.append(make_para_row(row))

    def add_array(self, array):
        self.extend(make_para_array(array))

    def add_header_row(self, row):
        self.add_row(map(lambda x: '<b>%s</b>' % x, row))

    def get_table(self, style, **kw):
        return Table(self, style=style, **kw)

    def get_long_table(self, style, **kw):
        return LongTable(self, style=style, **kw)
