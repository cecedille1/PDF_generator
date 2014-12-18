#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import mock


from pdf_generator.table import (
    FormattedTableGenerator,
    Styles,
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
