#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '0.1.1'

from reportlab.platypus import Paragraph, Spacer, Table, SimpleDocTemplate, Image, PageBreak, LongTable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import units, colors, enums, pagesizes

styles = getSampleStyleSheet()

styles.add(
    ParagraphStyle('right', parent=styles['Normal'], alignment=enums.TA_RIGHT))
styles.add(
    ParagraphStyle('centered', parent=styles['Normal'], alignment=enums.TA_CENTER))
styles.add(ParagraphStyle('boxed', parent=styles['Normal'],
                          borderWidth=1, borderColor=colors.black, bottomPadding=5 * units.mm,
                          borderPadding=5 * units.mm))
snormal = styles['Normal']


class PDFGenerator(list):

    def add_normal_paragraph(self, para):
        self.append(Paragraph(para, snormal))

    def add_centered_paragraph(self, para):
        self.append(Paragraph(para, styles['centered']))

    def add_right_paragraph(self, para):
        self.append(Paragraph(para, styles['right']))

    def add_horiz_spacer(self, size):
        self.append(Spacer(0, size * units.mm))

    def add_boxed_paragraph(self, para, size):
        self.append(Table([[Paragraph(para, styles['boxed'])]],
                          colWidths=(size * units.mm,),
                          hAlign=enums.TA_RIGHT))

    def build(self, filename, title=''):
        doc = SimpleDocTemplate(filename, pagesize=pagesizes.A4,
                                rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=18,
                                author='MusiboxLive', title=title)
        doc.build(self)

    def add_picture(self, filename, width=None, height=None):
        self.append(Image(filename, height=height, width=width))

    def add_title(self, n, content):
        self.append(Paragraph(content, styles['h%i' % n]))

    def new_page(self):
        self.append(PageBreak())


def make_para(x):
    return Paragraph(x, snormal)


def make_para_row(x):
    return map(make_para, x)


def make_para_array(x):
    return map(make_para_row, x)


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
