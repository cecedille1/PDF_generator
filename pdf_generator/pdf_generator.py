#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from reportlab.platypus import Paragraph, Spacer, Table, SimpleDocTemplate, Image, PageBreak
from reportlab.lib import units, enums, pagesizes

from pdf_generator.styles import styles, make_para


class PDFGenerator(list):

    def add_normal_paragraph(self, para):
        self.append(make_para(para))

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
