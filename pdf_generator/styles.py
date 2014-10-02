#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import units, colors, enums
from reportlab.platypus import Paragraph


styles = getSampleStyleSheet()

styles.add(ParagraphStyle(
    'right',
    parent=styles['Normal'],
    alignment=enums.TA_RIGHT
))
styles.add(ParagraphStyle(
    'centered',
    parent=styles['Normal'],
    alignment=enums.TA_CENTER
))
styles.add(ParagraphStyle(
    'boxed',
    parent=styles['Normal'],
    borderWidth=1,
    borderColor=colors.black,
    bottomPadding=5 * units.mm,
    borderPadding=5 * units.mm,
))


snormal = styles['Normal']


def make_para(x):
    return Paragraph(x, snormal)


def make_para_row(x):
    return map(make_para, x)


def make_para_array(x):
    return map(make_para_row, x)
