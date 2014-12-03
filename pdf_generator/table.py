#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tables
======

The table generation process use a :class:`TableGenerator` to gather all the
cells of the table. The methods :meth:`TableGenerator.get_table` and
:meth:`TableGenerator.get_long_table` returns the flowable objects to add to
the story.

Those methods take a list of styles, used to create a
:class:`reportlab.platypus.TableStyle` object for the table. Those styles are
are tuples as defined by :mod:`reportlab`.

The :class:`Styles` objects and its default instantiation :data:`styles` are
shortcut to :mod:`reportlab` table styles in a less obnoxious interface.

Example:

>>> gen = TableGenerator()
>>> gen.append([
...     'Column 1',
...     'Column 2',
... ])
>>> gen.extend(datas)
>>> story.append(gen.get_long_table(
...     styles.first_row.TextColor(colors.red),
...     styles.first_col.Alignment('RIGHT'),
... ))

.. data:: styles

    A shortcut to create :mod:`reportlab` table styles. All attributes of
    styles objects correspond to table styles directive and the arguments are
    the parameters of thoses table styles.

    Arguments are concatenated and may be applied before or after setting the
    directive name.

    Those 4 directives are equivalent:

    >>> styles((-1, 0), (-1, -1), 1, colors.black).Grid()
    >>> styles.Grid((-1, 0), (-1, -1), 1, colors.black)
    >>> styles((-1, 0), (-1, -1)).Grid(1, colors.Black)
    >>> ('GRID', (-1, 0), (-1, -1), 1, colors.black)

    This allow to create predefined sections of the grid and apply different
    styles to those sections.

    The sections **first_row**, **first_col**, **last_row**, **last_col** are
    predefined styles for respectively the first row, the first column, the
    last row and the last column. **first_rows**, **last_rows**,
    **first_cols**, **last_cols** are function matching the first and last columns
    or rows up the given value.

    Those 3 directives are equivalent:

    >>> styles((-2, 0), (-1, -1)).Background(colors.red)
    >>> styles.last_cols(2).Background(colors.red)
    >>> ('BACKGROUND', (-2, 0), (-1, -1), colors.red)

    The **all** attributes is a shorcut to a section for all the table.

    A special **styles.grid** style is defined and mainly designed for quick
    debugging more than intended as a production value. It defines a black grid
    on each cell of the array.
"""

from __future__ import absolute_import

import collections

from reportlab.lib import colors
from reportlab.platypus import (
    Table,
    LongTable,
    TableStyle,
    Paragraph as ParagraphClass
)


__all__ = [
    'TableGenerator',
    'styles'
]


class TableGenerator(collections.MutableSequence):
    """
    A Generator of :class:`Table` and :class:`LongTable`.

    This object is a mutable sequence and supports all the access as a list to
    add values.
    """

    def __init__(self, size=None):
        self._size = size
        self.content = list()

    @property
    def size(self):
        if self._size:
            return self._size
        return max(len(x) for x in self)

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

    def get_table(self, *style, **kw):
        """
        Returns the table as a :class:`reportlab.platypus.Table`
        """
        return Table(self.content, style=TableStyle(style), **kw)

    def get_long_table(self, *style, **kw):
        """
        Returns the table as a :class:`reportlab.platypus.LongTable`.

        The :class:`LongTable` is recommended for bigger tables.
        """
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
        'textcolor': 3,

        'span': 2,
    }

    def __init__(self, *args):
        self.args = args

    def __getattr__(self, name):
        return CellsStyle(name, self.known_styles.get(name.lower()), self.args)


class CellsStyle(object):
    def __init__(self, name, argc, args):
        self.name = name.upper()
        self.argc = argc
        self.args = args

    def __call__(self, *args):
        args = self.args + args

        if self.argc is not None and len(args) != self.argc:
            raise TypeError('{2}: Expecting {0} arguments, got {1}'.format(
                self.argc, len(args), self.name))
        return (self.name, ) + args


styles = Styles()

styles.all = Styles((0, 0), (-1, -1))

styles.first_row = Styles((0, 0), (-1, 0))
styles.first_rows = lambda x: Styles((0, 0), (-1, x))

styles.last_row = Styles((0, -1), (-1, -1))
styles.last_rows = lambda x: Styles((0, -x), (-1, -1))

styles.first_col = Styles((0, 0), (0, -1))
styles.first_cols = lambda x: Styles((0, 0), (x, -1))

styles.last_col = Styles((-1, 0), (-1, -1))
styles.last_cols = lambda x: Styles((-x, 0), (-1, -1))

styles.grid = styles.all.Grid(1, colors.black)
