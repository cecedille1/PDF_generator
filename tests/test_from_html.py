#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import mock

from pdf_generator import Paragraph
from pdf_generator.from_html import Parser


class TestParser(unittest.TestCase):
    def setUp(self):
        self.medias = mock.Mock()
        self.links = mock.Mock()

        self.p = Parser(self.medias, self.links)

    def parse(self, text):
        self.p.feed(text)
        return self.p.get_result()

    def test_empty(self):
        self.assertEqual(self.parse(''), [])

    def test_paragraph(self):
        self.assertEqual(self.parse('text'), [Paragraph('text')])

    def test_paragraph_br(self):
        self.assertEqual(self.parse('text<br />taxt'), [Paragraph('text<br />taxt')])

    def test_image(self):
        self.medias.return_value = '/static/source.png'
        with mock.patch('pdf_generator.from_html.Image') as Image:
            self.assertEqual(self.parse('<img src="source.png" />'), [
                Image.return_value
            ])
        Image.assert_called_once_with('/static/source.png', width=None, height=None)
        self.medias.assert_called_once_with('source.png')

    def test_image_dimension(self):
        self.medias.return_value = '/static/source.png'
        with mock.patch('pdf_generator.from_html.Image') as Image:
            self.assertEqual(self.parse('<img src="source.png" width="100" height="200" />'), [
                Image.return_value
            ])
        Image.assert_called_once_with('/static/source.png', width=100, height=200)
        self.medias.assert_called_once_with('source.png')

    def test_link(self):
        self.links.return_value = 'location'
        self.assertEqual(self.parse('<a href="abc">text</a>'),
                         [Paragraph('<link href="location">text</link>')])
        self.links.assert_called_once_with('abc')

    def test_paragraph_title(self):
        self.assertEqual(
            self.parse('<h1>Title</h1><h2>Subtitle</h2><p>Text</p>'), [
                Paragraph('Title', 'h1'),
                Paragraph('Subtitle', 'h2'),
                Paragraph('Text'),
            ])

    def test_paragraph_rich_text(self):
        self.links.return_value = '/this/'
        self.assertEqual(
            self.parse('<h1>Title</h1><p>Text <strong>strong</strong> <a href="/this/">That</a> also</p>'), [
                Paragraph('Title', 'h1'),
                Paragraph('Text <b>strong</b> <link href="/this/">That</link> also'),
            ])

    def test_center(self):
        with mock.patch('pdf_generator.from_html.Table') as Table:
            self.assertEqual(
                self.parse('<center><h1>Title</h1><p>Text <em>strong</em> also</p></center>'),
                [Table.return_value])

        Table.assert_called_once_with([
            [Paragraph('Title', 'h1', alignment=1)],
            [Paragraph('Text <i>strong</i> also', alignment=1)],
        ],
            style=mock.ANY
        )

    def test_ul(self):
        self.assertEqual(
            self.parse('<ul><li>pif</li><li>paf</li><li>pouf</li></ul>'), [[
                Paragraph('pif', bulletText='-'),
                Paragraph('paf', bulletText='-'),
                Paragraph('pouf', bulletText='-'),
            ]])

    def test_paragraph_ul(self):
        self.assertEqual(
            self.parse('<p>Text <strong>pre</strong><ul><li>pif</li></ul> Text <em>post</em></p>'), [
                Paragraph('Text <b>pre</b>'),
                [Paragraph('pif', bulletText='-')],
                Paragraph('Text <i>post</i>'),
            ])

    def test_paragraph_image(self):
        with mock.patch('pdf_generator.from_html.Image') as Image:
            parsed = self.parse('<ul><li>pif</li><li><img src="image.png" /></li></ul>')

        self.assertEqual(parsed, [[
            Paragraph('pif', bulletText='-'),
            Image.return_value,
        ]])
