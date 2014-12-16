#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import mock

from pdf_generator import Paragraph
from reportlab.platypus import Frame
from pdf_generator.templates import (
    Fraction,
    BaseTemplate,
    TemplateRows,
    Template
)


class TestFraction(unittest.TestCase):
    def test_repr_3_4(self):
        f = Fraction(.75)
        self.assertEqual(repr(f), '3/4')

    def test_repr_0(self):
        f = Fraction(0)
        self.assertEqual(repr(f), '0/0')

    def test_add(self):
        self.assertEqual(Fraction(1/2.) + Fraction(1/4.), Fraction(3/4.))

    def test_add_0(self):
        self.assertEqual(0 + Fraction(1/2.), Fraction(1/2.))

    def test_mul(self):
        self.assertEqual(Fraction(0.75) * 100, 75)


class TestBaseTemplateExplode(unittest.TestCase):
    def setUp(self):
        self.bt = BaseTemplate()

    def test_explode_0(self):
        self.assertEqual(self.bt.explode(1), (1, 1, 1, 1))

    def test_explode_1(self):
        self.assertEqual(self.bt.explode((1,)), (1, 1, 1, 1))

    def test_explode_2(self):
        self.assertEqual(self.bt.explode((1, 2)), (1, 2, 1, 2))

    def test_explode_3(self):
        self.assertEqual(self.bt.explode((1, 2, 3)), (1, 2, 3, 2))

    def test_explode_4(self):
        self.assertEqual(self.bt.explode((1, 2, 3, 4)), (1, 2, 3, 4))


class TestBaseTemplatePageEnd(unittest.TestCase):
    def setUp(self):
        """
          40      180
           |       |    200, 300
        +-------------+
        |      10     |
        |  +-------+  | - 290
        | 4|       |2 |
        | 0|       |0 |
        |  +-------+  | - 30
        |      30     |
        +-------------+
        """

        self.kw = {}

    def bt(self):
        return BaseTemplate(
            pagesize=(200, 300),
            margins=(10, 20, 30, 40),
            **self.kw
        )

    def test_printable_height(self):
        self.assertEqual(self.bt().printable_height, 260)

    def test_printable_width(self):
        self.assertEqual(self.bt().printable_width, 140)

    def test_header(self):
        self.kw['header'] = header = mock.Mock(Paragraph, style=mock.Mock(
            borderColor='red',
            textColor='blue'))
        header.wrapOn.side_effect = lambda c, w, h: (w, h)

        canvas = mock.Mock()
        self.bt().page_end(canvas, mock.Mock())

        canvas.assert_has_calls([
            mock.call.setStrokeColor('blue'),
            mock.call.setStrokeColor('red'),
            mock.call.line(40, 290, 180, 290),
        ])
        header.drawOn.assert_called_once_with(
            canvas, 0, 290
        )

    def test_footer(self):
        canvas = mock.Mock()
        self.kw['footer'] = footer = mock.Mock(Paragraph, style=mock.Mock(borderColor=None, textColor='blue'))
        footer.wrapOn.side_effect = lambda c, w, h: (w, h)

        self.bt().page_end(canvas, mock.Mock())

        self.assertFalse(canvas.line.called)
        canvas.setStrokeColor.assert_called_once_with('blue')
        footer.drawOn.assert_called_once_with(
            canvas, 0, 0
        )


class TestTemplateRows(unittest.TestCase):
    def setUp(self):
        self.tr = TemplateRows()

    def test_absolute(self):
        self.tr.row(1).cell()
        self.tr.row(1).cell()
        self.tr.row(1).cell()
        self.assertEqual(list(self.tr), [
            (0, 0, None, 1),
            (0, 1, None, 1),
            (0, 2, None, 1),
        ])

    def test_fraction(self):
        self.tr.row(Fraction(0.3)).cell()
        self.tr.row(Fraction(0.3)).cell()
        self.tr.row(Fraction(0.3)).cell()
        self.assertEqual(list(self.tr), [
            (0, 0, None, Fraction(0.3)),
            (0, Fraction(0.3), None, Fraction(0.3)),
            (0, Fraction(0.6), None, Fraction(0.3)),
        ])

    def test_split_in(self):
        self.tr.row(1).split(3)
        self.assertEqual(list(self.tr), [
            (Fraction(0), 0, Fraction(1/3.), 1),
            (Fraction(1/3.), 0, Fraction(1/3.), 1),
            (Fraction(2/3.), 0, Fraction(1/3.), 1),
        ])

    def test_split(self):
        self.tr.row(1).split(1, 2, 3)
        self.assertEqual(list(self.tr), [
            (Fraction(0), 0, Fraction(1/6.), 1),
            (Fraction(1/6.), 0, Fraction(1/3.), 1),
            (Fraction(1/2.), 0, Fraction(1/2.), 1),
        ])

    def test_row_skip(self):
        self.tr.row(1).cell(2)
        self.tr.skip(4)
        self.tr.row(3).cell(4)

        self.assertEqual(list(self.tr), [
            (0, 0, 2, 1),
            (0, 5, 4, 3),
        ])

    def test_cell(self):
        self.tr.row(1).cell(2)
        self.tr.row(3).cell(4)

        self.assertEqual(list(self.tr), [
            (0, 0, 2, 1),
            (0, 1, 4, 3),
        ])

    def test_cell_skip(self):
        self.tr.row(1).cell(2).skip(3).cell(4)
        self.assertEqual(list(self.tr), [
            (0, 0, 2, 1),
            (5, 0, 4, 1),
        ])

    def test_row_none(self):
        self.tr.row(1).cell(1)
        self.tr.row().cell(2)
        self.assertEqual(list(self.tr), [
            (0, 0, 1, 1),
            (0, 1, 2, None),
        ])

        with self.assertRaises(ValueError):
            self.tr.row(1)

    def test_cell_none(self):
        row = self.tr.row(1)
        row.cell()
        with self.assertRaises(ValueError):
            row.cell()

    def test_cell_split(self):
        row = self.tr.row(1)
        row.cell(1)
        with self.assertRaises(ValueError):
            row.split(1)


class TestTemplate(unittest.TestCase):
    def setUp(self):
        self.template = Template(pagesize=(200, 300), margins=(10, 20, 30, 40))

    def test_whole_page(self):
        with mock.patch('pdf_generator.templates.Frame', spec=Frame) as mFrame:
            self.template.add_whole_page(padding=0)

        mFrame.assert_called_once_with(40, 30, 140, 260,
                                       topPadding=0,
                                       bottomPadding=0,
                                       leftPadding=0,
                                       rightPadding=0,
                                       )

    def test_split_absolute(self):
        """
          40  80  180
           |  |    |    200, 300
        +-------------+
        |  +--+----+  | - 290
        |  |1 | 2  |  |
        |  +--+----+  | - 190
        |  |   3   |  |
        |  +-------+  | - 90
        |  |   4   |  |
        |  +-------+  | - 30
        +-------------+
        """

        with mock.patch('pdf_generator.templates.Frame', spec=Frame) as mFrame:
            self.template.add_page([
                (0, 0, 40, 100),  # 1
                (40, 0, None, 100),  # 2

                (0, 100, 1000, 100),  # 3
                (0, 200, None, None),
            ], padding=0)

        mFrame.assert_has_calls([
            mock.call(40, 190, 40, 100,
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
            mock.call(80, 190, 100, 100,
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
            mock.call(40, 90, 140, 100,
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
            mock.call(40, 30, 140, 60,
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
        ])

    def test_split_fraction(self):

        with mock.patch('pdf_generator.templates.Frame', spec=Frame) as mFrame:
            self.template.add_page([
                (0, 0, Fraction(2/7.), 100),
                (Fraction(2/7.), 0, Fraction(5/7.), 100),
                (Fraction(1/4.), Fraction(1/4.), Fraction(1/2.), Fraction(1/2.)),
            ], padding=0)

        mFrame.assert_has_calls([
            mock.call(40, 190, 40, 100,
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
            mock.call(80, 190, 100, 100,
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
            mock.call(75, 95, 70, 130,
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
        ])

    def test_frame_overflow(self):
        with mock.patch('pdf_generator.templates.Frame', spec=Frame) as mFrame:
            self.template.add_page([
                (0, 0, 200, 300),
                (-100, -100, 400, 500),
            ], padding=0)

        mFrame.assert_has_calls([
            mock.call(40, 30, 140, 260,
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
            mock.call(40, 30, 140, 260,
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
        ])
