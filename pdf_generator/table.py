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
    TableStyle as RootTableStyle,
)


__all__ = [
    'TableGenerator',
    'TableStyle',
    'styles'
]


class TableGenerator(collections.MutableSequence):
    """
    A Generator of :class:`Table` and :class:`LongTable`.

    This object is a mutable sequence and supports all the access as a list to
    add values.
    """

    def __init__(self, *styles, **kw):
        self.content = list()
        style = kw.pop('style', None)

        if styles:
            style = RootTableStyle(styles, parent=style)

        self.base_style = style
        self.default_kw = kw

    def __len__(self):
        return len(self.content)

    def __iter__(self):
        return iter(self.content)

    def __setitem__(self, index, value):
        self.content[index] = value

    def __getitem__(self, index):
        return self.content[index]

    def __delitem__(self, index):
        del self.content[index]

    def insert(self, index, value):
        self.content.insert(index, value)

    def _build(self, cls, style, kw):
        if style:
            style = RootTableStyle(style, parent=self.base_style)
        else:
            style = self.base_style
        h_align = kw.pop('hAlign', None)

        keywords = dict(self.default_kw)
        kw['style'] = style
        keywords.update(kw)

        table = cls(self.content, **keywords)

        if h_align is not None:
            table.hAlign = h_align

        return table

    def get_table(self, *style, **kw):
        """
        Returns the table as a :class:`reportlab.platypus.Table`
        """
        return self._build(Table, style, kw)

    def get_long_table(self, *style, **kw):
        """
        Returns the table as a :class:`reportlab.platypus.LongTable`.

        The :class:`LongTable` is recommended for bigger tables.
        """
        return self._build(LongTable, style, kw)


class FormattedTableGenerator(TableGenerator):
    """
    :class:`TableGenerator` that formats the rows appended with format strings.
    **formats** is a list of ``None`` or template strings. ``None`` means that
    the values is copied as given. Template strings are format strings
    compatible with the builtin :func:`format` function.

    >>> ftg = FormattedTableGenerator([None, '.2f', '.0%'])
    >>> ftg.append_raw(['name', 'Value', 'Rate'])
    >>> ftg.append(['value1', 513.492, 0.03])
    >>> ftg.append(['value2', 1016.2, 0.43])
    >>> ftg.get_table()

    Giving::

        Name    | Value     | Rate
        value1  |    513.49 |   3%
        value2  |   1016.20 |  43%
    """
    def __init__(self, formats, *args, **kw):
        super(FormattedTableGenerator, self).__init__(*args, **kw)
        self.formats = formats

    def append_raw(self, values):
        super(FormattedTableGenerator, self).append(values)

    def append(self, values):
        formatted = [v if f is None else format(v, f)
                     for (f, v) in zip(self.formats, values)]
        super(FormattedTableGenerator, self).append(formatted)


class TableStyle(RootTableStyle, object):
    def __init__(self, *args):
        super(TableStyle, self).__init__(args)


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

    def __repr__(self):
        return 'Styles({})'.format(', '.join(repr(x) for x in self.args))

    def __getattr__(self, name):
        return CellsStyle(name, self.known_styles.get(name.lower()), self.args)

    def __eq__(self, other):
        if isinstance(other, Styles):
            other = other.args
        elif not isinstance(other, (tuple, list)):
            return NotImplemented
        return self.args == other


class CellsStyle(object):
    def __init__(self, name, argc, args):
        self.name = name.upper()
        self.argc = argc
        self.args = args

    def __repr__(self):
        return '{}({})'.format(self.name.capitalize(), self.args)

    def __call__(self, *args):
        args = self.args + args

        if self.argc is not None and len(args) != self.argc:
            raise TypeError('{2}: Expecting {0} arguments, got {1}'.format(
                self.argc, len(args), self.name))
        return (self.name, ) + args

    def __eq__(self, other):
        return (isinstance(other, CellsStyle) and
                self.name == other.name and
                self.args == other.args)


class AllStyles(Styles):
    @property
    def grid(self):
        return self.all.Grid(1, colors.black)

    @property
    def all(self):
        return self.cols(0, -1)

    @property
    def first_row(self):
        return self.rows(0, 0)

    def first_rows(self, n):
        return self.rows(0, n)

    def row(self, n):
        return self.rows(n, n)

    def rows(self, first, last):
        return Styles((0, first), (-1, last))

    @property
    def last_row(self):
        return self.rows(-1, -1)

    def last_rows(self, n):
        return self.rows(-n, -1)

    @property
    def first_col(self):
        return self.cols(0, 0)

    def first_cols(self, n):
        return self.cols(0, n)

    def col(self, n):
        return self.cols(n, n)

    def cols(self, first, last):
        return Styles((first, 0), (last, -1))

    @property
    def last_col(self):
        return self.cols(-1, -1)

    def last_cols(self, n):
        return self.cols(-n, -1)


styles = AllStyles()
