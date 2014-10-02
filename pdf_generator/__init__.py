#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__version__ = '0.2.1'

__all__ = [
    'PDFGenerator',
    'TableGenerator',
    'make_para',
    'Paragraph',
]

from pdf_generator.styles import make_para
from pdf_generator.table import TableGenerator
from pdf_generator.pdf_generator import PDFGenerator

Paragraph = make_para
