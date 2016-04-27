#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import mock


from reportlab.lib import colors
from pdf_generator.table import (
    FormattedTableGenerator,
    Styles,
    AllStyles,
    CellsStyle,
)


class TestFormattedTableGenerator(unittest.TestCase):
    def setUp(self):
        self.fpg = FormattedTableGenerator([None, '05.2f'])

    def test_append_raw(self):
        m1, m2 = mock.Mock(), mock.Mock()
        self.fpg.append_raw([m1, m2])
        self.assertEqual(list(self.fpg), [[m1, m2]])

    def test_append(self):
        m1 = mock.Mock()
        self.fpg.append([m1, 4.4])
        self.assertEqual(list(self.fpg), [[m1, '04.40']])


class TestAllStyles(unittest.TestCase):
    def setUp(self):
        self.styles = AllStyles()

    def test_grid(self):
        self.assertEqual(self.styles.grid, CellsStyle('grid', None, ((0, 0), (-1, -1)))(1, colors.black))

    def test_all(self):
        self.assertEqual(self.styles.all, Styles((0, 0), (-1, -1)))

    def test_first_row(self):
        self.assertEqual(self.styles.first_row, Styles((0, 0), (-1, 0)))

    def test_first_rows(self):
        self.assertEqual(self.styles.first_rows(4), Styles((0, 0), (-1, 4)))

    def test_row(self):
        self.assertEqual(self.styles.row(4), Styles((0, 4), (-1, 4)))

    def test_rows(self):
        self.assertEqual(self.styles.rows(2, 5), Styles((0, 2), (-1, 5)))

    def test_last_row(self):
        self.assertEqual(self.styles.last_row, Styles((0, -1), (-1, -1)))

    def test_last_rows(self):
        self.assertEqual(self.styles.last_rows(4), Styles((0, -4), (-1, -1)))

    def test_first_col(self):
        self.assertEqual(self.styles.first_col, Styles((0, 0), (0, -1)))

    def test_first_cols(self):
        self.assertEqual(self.styles.first_cols(4), Styles((0, 0), (4, -1)))

    def test_col(self):
        self.assertEqual(self.styles.col(4), Styles((4, 0), (4, -1)))

    def test_cols(self):
        self.assertEqual(self.styles.cols(2, 5), Styles((2, 0), (5, -1)))

    def test_last_col(self):
        self.assertEqual(self.styles.last_col, Styles((-1, 0), (-1, -1)))

    def test_last_cols(self):
        self.assertEqual(self.styles.last_cols(4), Styles((-4, 0), (-1, -1)))


class TestStyle(unittest.TestCase):
    def test_uppercase(self):
        styles = Styles()
        self.assertEqual(styles.attribute(), ('ATTRIBUTE', ))

    def test_save_args(self):
        styles = Styles(1, 2)
        self.assertEqual(styles.attribute(), ('ATTRIBUTE', 1, 2))

    def test_takes_args(self):
        styles = Styles()
        self.assertEqual(styles.attribute(3, 4), ('ATTRIBUTE', 3, 4))

    def test_merge_args(self):
        styles = Styles(1, 2)
        self.assertEqual(styles.attribute(3, 4), ('ATTRIBUTE', 1, 2, 3, 4))

    def test_count_args(self):
        styles = Styles()
        self.assertEqual(styles.span(1, 2), ('SPAN', 1, 2))

    def test_raise_if_not_args(self):
        styles = Styles()
        self.assertRaises(TypeError, styles.span, 1)

    def test_count_merged(self):
        styles = Styles(1)
        self.assertEqual(styles.span(2), ('SPAN', 1, 2))
