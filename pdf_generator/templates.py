# -*- coding: utf-8 -*-

"""
Templates and frames
====================

The :class:`SimpleTemplate` defines a simple template with a whole page.

The more advanced :class:`Template` cuts the page in frames. The template is
build by adding pages with :meth:`Template.add_page`. The pages can be defined
by a list of tuples of positions, width and height creating frames.

Both `SimpleTemplate` and `Template` are thread-safe and re-usable. The
:class:`BaseDocTemplate` they produce are single use.

The class :class:`TemplateRows` are builder objects to create easily frames.
The defines rows and split them in cells.

Example: A A4 page with 1 cm margin on all the borders and split in 5 frames::

    +-----+-----+
    | F1  | F2  |
    +-----+-----+
    |           |
    +----+-+----+
    | F3 | | F4 |
    |    | |    |
    +----+-+----+
    |           |
    |    F5     |
    |           |
    +-----------+

>>> template = Template(pagesizes.A4, 1 * units.cm)

>>> tr = TemplateRows()
>>> tr.row(4 * units.cm).split(2)  # 4 cm split in 2 equals part F1 anf F2
>>> tr.row(2 * units.cm)  # Empty space of 2 cm
>>> tr.row(5 * units.cm).cell(Fraction(2/5.)).skip(Fraction(1/5.)).cell()
>>> # 5 cm split in 2 sections, of 2/5 of the page separated by an empty space F3 and F4
>>> tr.row().cell() # The rest F5
>>> template.add_page(tr)

The switch from a frame to the next is triggered either when the frame is full
or when a :class:`FrameBreak` special flowable is inserted to the story. The
:class:`Story` has the shortcut method: `meth:Story.next_frame`.

Callbacks
---------

Templates have a set of post-processing options. There two *page_end* general
purpose callbacks and two sets of *header* and *footer*.

Page_end
********

Two callbacks can be set and are executed after each page have been rendered.
The first one is set at the instantiation of the :class:`SimpleTemplate` or
:class:`Template`. The other one is set at call time when the
:class:`reportlab.platypus.BaseDocTemplate` is created.

They have a general purpose and can alter the canvas.

Header and footer
*****************

Header and footer are optional :class:`reportlab.platypus.Paragraph` instances
that are written in respectively the top and bottom margins of the document. As
for page_end, two headers can be given, one at instantiation time and one at
the call time when the :class:`BaseDocTemplate` is created.

If a borderColor style is set, a line is also added between the header or
the footer and the rest of the page.


>>> t = SimpleTemplate(margins=(50, 10),
...               header=Paragraph('header header',
...                                textColor=colors.green,
...                                fontSize=8,
...                                alignment=enums.TA_CENTER,
...                                ),
...               footer=Paragraph('footer footer',
...                                textColor=colors.blue,
...                                fontSize=8,
...                                borderColor=colors.red,
...                                alignment=enums.TA_CENTER,
...                                ),
...               )

Results:
    +-------------------+
    |   header header   | < green
    |                   |
    |                   |
    |                   |
    |                   |
    | ----------------  | < red
    |   footer footer   | < blue
    +-------------------+

"""

import six
import collections
from reportlab.platypus import (
    Frame,
    BaseDocTemplate,
    PageTemplate,
    SimpleDocTemplate,
)
from reportlab.lib import pagesizes

__all__ = [
    'BaseTemplate',
    'SimpleTemplate',
    'Template',
    'Fraction',
    'TemplateRows',
    'TemplateRow',
]


PageTemplateSpec = collections.namedtuple('PageTemplateSpec', ['id', 'frames'])


def noop(canvas, doc):
    """Callback for page_end"""
    pass


class Fraction(object):
    """
    Fraction of *ratio*.
    """
    def __init__(self, ratio):
        self._ratio = ratio

    def __mul__(self, x):
        return x * self._ratio

    def __radd__(self, other):
        return self.__add__(other)

    def __add__(self, x):
        if x == 0:
            return self
        if not isinstance(x, Fraction):
            raise ValueError('Can only add a fraction to a fraction')
        return Fraction(x._ratio + self._ratio)

    def __eq__(self, other):
        return isinstance(other, Fraction) and self._ratio == other._ratio

    def __repr__(self):
        if self._ratio == 0:
            return '0/0'
        for x in six.moves.range(2, 20):
            if self._ratio * x % 1 == 0.0:
                return '{0}/{1}'.format(int(self._ratio * x), x)
        return str(self._ratio)


class BaseTemplate(object):
    def __init__(self, pagesize=None, margins=None, page_end=None, header=None, footer=None):
        self.width, self.height = pagesize or pagesizes.A4
        margins = margins or (36, 36, 18)
        self._mtop, self._mright, self._mbottom, self._mleft = self.explode(margins)

        self.left = self._mleft
        self.right = self.width - self._mright
        self.top = self.height - self._mtop
        self.bottom = self._mbottom

        self.page_templates = []

        self._page_end = self._wraps_page_end(page_end)
        self._header = self._get_top_write_margin_callback(header)
        self._footer = self._get_bottom_write_margin_callback(footer)

    def _wraps_page_end(self, fn):
        if fn is None:
            return noop

        def wrapped_page_end(canvas, doc):
            canvas.saveState()
            fn(canvas, doc)
            canvas.restoreState()
        return wrapped_page_end

    def get_page_end(self, page_end_fn=None, header=None, footer=None):
        page_end_fn = self._wraps_page_end(page_end_fn)

        footer_callback = self._get_bottom_write_margin_callback(footer)
        header_callback = self._get_top_write_margin_callback(header)

        def page_end(canvas, doc):
            self._page_end(canvas, doc)
            self._header(canvas, doc)
            self._footer(canvas, doc)

            page_end_fn(canvas, doc)
            footer_callback(canvas, doc)
            header_callback(canvas, doc)

        return page_end

    def _get_bottom_write_margin_callback(self, footer):
        return self._get_write_margin_callback(self._mbottom, self.bottom, 0, footer)

    def _get_top_write_margin_callback(self, header):
        return self._get_write_margin_callback(self._mtop, self.top, self.top, header)

    def _get_write_margin_callback(self, margin, line_y, text_y, p):
        if p is None:
            return noop

        def write_margin(canvas, doc):
            w, h = p.wrapOn(canvas, self.printable_width, margin)

            canvas.saveState()
            canvas.setStrokeColor(p.style.textColor)
            p.drawOn(canvas, (self.printable_width - w) / 2, text_y + (margin - h) / 2)

            if p.style.borderColor is not None:
                canvas.setStrokeColor(p.style.borderColor)
                canvas.line(self.left, line_y, self.right, line_y)

            canvas.restoreState()
        return self._wraps_page_end(write_margin)

    def explode(self, margins):
        """
        Explode a value or a tuple in 4 values as CSS borders, paddings and
        margins
        """
        if not isinstance(margins, (tuple, list)):
            margins = [margins]

        if len(margins) == 1:
            mleft = mright = mtop = mbottom = margins[0]
        elif len(margins) == 2:
            mbottom, mright = margins
            mleft = mright
            mtop = mbottom
        elif len(margins) == 3:
            mtop, mright, mbottom = margins
            mleft = mright
        elif len(margins) == 4:
            mtop, mright, mbottom, mleft = margins
        else:
            raise ValueError('Bad values for margins')
        return mtop, mright, mbottom, mleft

    @property
    def printable_width(self):
        """
        The width of the printable area, excluding the margins
        """
        return self.width - self._mleft - self._mright

    @property
    def printable_height(self):
        """
        The height of the printable area, excluding the margins
        """
        return self.height - self._mtop - self._mbottom

    @property
    def pagesize(self):
        return (self.width, self.height)

    def __call__(self, out, title, author, debug=False, page_end=None):
        raise NotImplementedError('This method should return a DocTemplate')


class SimpleTemplate(BaseTemplate):
    """
    The simplest template, a page of *pagesize* with margin *margins*.
    """
    def __call__(self, out, title, author, debug=False,
                 page_end=None, header=None, footer=None):
        template = SimpleDocTemplate(out,
                                     pagesize=self.pagesize,
                                     rightMargin=self._mright,
                                     leftMargin=self._mleft,
                                     topMargin=self._mtop,
                                     bottomMargin=self._mbottom,
                                     author=author,
                                     title=title,
                                     showBoundary=debug,
                                     )

        page_end = self.get_page_end(page_end, header, footer)
        template.onFirstPage = page_end
        template.onLaterPages = page_end
        return template


class TemplateRows(object):
    """
    A builder of templates, row by row.

    :class:`TemplateRows` are stateful and spaces are allocated with :meth:`row`
    and `skip` from the top to the bottom.

    Each row does not overlap with row under or over it. All the cells of a row
    have the same height.

    .. note::

        The *height* arguments of :meth:`skip` and :meth:`row` are either
        :class:`int` or :class:`float`, or :class:`Fraction` relative to the
        :attr:`printable_height` of the template. The usage of each of the method
        must be consistent in all the rows of the :class:`TemplateRows`.
    """

    def __init__(self):
        self._rows = []
        self._current_height = 0

    def skip(self, height):
        """
        Skip *height* of rows.
        """
        self._current_height = height + self._current_height
        return self

    def row(self, height=None):
        """
        Add a row of *height* in the template and returns a :class:`TemplateRow`.

        If *height* is ``None``, the whole page is used.
        """
        if self._current_height is None:
            raise ValueError('No space remaining')

        row = TemplateRow(self._current_height, height)
        if height is None:
            self._current_height = height
        else:
            self._current_height = height + self._current_height

        self._rows.append(row)
        return row

    def __iter__(self):
        for row in self._rows:
            for cell in row:
                yield cell


class TemplateRow(object):
    """
    A row of a :class:`TemplateRows`.
    """
    def __init__(self, y, height):
        self.y = y
        self.height = height
        self._cells = []
        self._consumed = 0

    def __iter__(self):
        for x, width in self._cells:
            yield x, self.y, width, self.height

    def skip(self, width):
        """
        Skip *width* of cell.
        """
        self._consumed = width + self._consumed
        return self

    def cell(self, width=None):
        """
        Create a Frame at this place of *width*.

        If *width* is None, the width takes all the remaining place.
        """
        if self._consumed is None:
            raise ValueError('No space left')

        self._cells.append((self._consumed, width))
        if width is None:
            self._consumed = None
        else:
            self._consumed = width + self._consumed
        return self

    def split(self, x, *args):
        """
        **split(x)**

        Split the row in *x* equal parts::

            row.split(2)

            +------+------+
            |  F1  |  F2  |
            +------+------+

        **split(x, y, z, ...)**

        Split the row in as many parts as arguments, weighed by each value::

            row.split(1, 3, 4, 2)

            +--+------+-------+----+
            |F1|  F2  |   F3  | F4 |
            +--+------+-------+----+

        .. note::

            :meth:`split` can only split empty rows. The methods :meth:`skip`
            or :meth:`cell` must not be called on the same row.
        """
        if self._cells:
            raise ValueError('Cannot split already divided cell')

        self._consumed = None

        if not args:
            args = [1] * x
        else:
            args = (x, ) + args

        total = float(sum(args))
        fractions = [Fraction(y/total) for y in args]

        acc = Fraction(0)
        for fraction in fractions:
            self._cells.append((acc, fraction))
            acc += fraction


class Template(BaseTemplate):
    """
    A template composed of frames.
    """
    def _resolve_dim(self, dim, ref):
        if dim is None:
            return ref
        elif isinstance(dim, Fraction):
            return dim * ref
        elif isinstance(dim, (int, float)):
            return dim

        raise ValueError('Unexpected {!r}, expected None, float, int, Fraction'.format(dim))

    def _get_frame(self, x, y, width, height, padding=None):
        # Invert the coordinates, from bottom left to top left
        width = self._resolve_dim(width, self.printable_width)
        height = self._resolve_dim(height, self.printable_height)

        x = self._resolve_dim(x, self.printable_width) + self._mleft
        y = self.height - self._resolve_dim(y, self.printable_height) - height - self._mtop

        if x < self.left:
            width -= self.left - x
            x = self.left
        if x + width > self.right:
            width = self.right - x

        if y < self.bottom:
            height -= self.bottom - y
            y = self.bottom

        if y + height > self.top:
            height = self.top - y

        ptop, pright, pbottom, pleft = self.explode(padding if padding is not None else 6)
        return Frame(x, y, width, height,
                     leftPadding=pleft,
                     topPadding=ptop,
                     bottomPadding=pbottom,
                     rightPadding=pright,
                     )

    def add_page(self, id, frame_defs=None, padding=None):
        """
        add_page([id,] frames_defs, padding=None)

        Adds a page to the template, composed of *frames_defs*. *id* is the
        title of the frame (referenceable by :meth:`Story.next_template`. When
        id is falsy or not specified a id is computed of the form _page-x where
        x is the number of the page.

        *frames_defs* is a list of tuples defining a frame. Each tuple is has a
        length of 4. The fields of the tuples are x, y, width and height. The
        x and y fields are relative to the top left corner of page. The width
        and height dimensension can be ``None`` meaning all the remaining of
        the page.

        Margins are enforced over the frame definitions and frames bigger than
        the printable height or width are silentry shrunk.
        """
        if frame_defs is None:
            frame_defs, id = id, None

        id = id or '_page-{0}'.format(len(self.page_templates))

        frames = [self._get_frame(*frame_def, padding=padding) for frame_def in frame_defs]
        pt = PageTemplateSpec(id, frames)

        self.page_templates.append(pt)
        return pt

    def add_whole_page(self, id=None, padding=None):
        """
        Add a page with a single frame taking the whole space.
        """
        return self.add_page(id, [(0, 0, None, None)], padding)

    def __call__(self, out, title, author, debug=False,
                 page_end=None, header=None, footer=None):
        page_end = self.get_page_end(page_end, header, footer)
        return BaseDocTemplate(
            out,
            pagesize=self.pagesize,
            pageTemplates=[PageTemplate(*pts, onPageEnd=page_end) for pts in self.page_templates],
            title=title,
            author=author,
            rightMargin=self._mright,
            leftMargin=self._mleft,
            topMargin=self._mtop,
            bottomMargin=self._mbottom,
            showBoundary=debug,
        )
