.. _Reportlab user guide: http://www.reportlab.com/docs/reportlab-userguide.pdf
.. _Reportlab documentation: http://www.reportlab.com/apis/reportlab/2.4/platypus.html#module-reportlab.platypus.doctemplate

=====
Usage
=====

Installation
============

PDF Generator requires :mod:`reportlab` and Python 2::

    pip install pdf_generator


Usage
=====

----------
Base setup
----------

The base object of a PDF generation is the story. The story is an instance
of :class:`pdf_generator.pdf_generator.Story` and contains the paragraphs,
tables, drawings, etc. Each story has a template. The template is a
:class:`pdf_generator.templates.Template` or a
:class:`pdf_generator.templates.SimpleTemplate`. The templates tells to the
builder where the elements should be rendered on a page.

The :class:`~pdf_generator.templates.SimpleTemplate` is a simple page where
all the surface, margins excepted is writeable.
The :class:`~pdf_generator.templates.Template` is a more advanced page where a
template can defines which spaces are writable within the page.

:class:`~pdf_generator.templates.SimpleTemplate` takes a page size and a
margin. Margins may be given as an number, or a tuple of 1, 2, 3 or 4 numbers.
A single number is interpreted as a 1 length tuple. Tuples are interpreted in
the same way as CSS does with margins, paddings, etc::

    margin=(x,)                     margin=(x, y)

        x                                 x
      +---+                             +---+
    x |   | x                         y |   | y
      +---+                             +---+
        x                                 x

    margin=(x, y, z)                margin=(x, y, z, t)

        x                                 x
      +---+                             +---+
    y |   | y                         t |   | y
      +---+                             +---+
        z                                 z


>>> from pdf_generator import Story, SimpleTemplate
>>> s = Story(SimpleTemplate())

-------
Content
-------

.. currentmodule:: pdf_generator.pdf_generator

Content is added to the story by
:meth:`appending<Story.append>` it to the story.

Text and style
--------------

The base text unit is the paragraph. A :mod:`reportlab` paragraph can contains
some basic markup. :mod:`pdf_generator.styles` contains a :class:`Paragraph`
shortcut to the :class:`Paragraph` of :mod:`reportlab` that eases the styling.

See the `Reportlab user guide`_ for the documentation
of paragraph styles.

>>> from pdf_generator.styles import Paragraph
>>> s.append(Paragraph('Hello world', 'h1', fontSize=15))
>>> s.append(Paragraph('pdf_generator is a simple and powerful lib to generate PDFs'))


Tables
------

Tables are simplified by :mod:`pdf_generator.table`. The tables are generated
by a :class:`pdf_generator.table.TableGenerator`. This object contains the
whole content of a table and apply styles on it.

A table is a list of rows, the rows are lists of cells. Cells can be strings,
Paragraph, other tables, images, etc can be added.

>>> from pdf_generator.table import TableGenerator
>>> table = Table()
>>> table.add_header_row(['Cat', 'Color', 'Number of lives'])
>>> table.extend([
...     ['Salem', 'black', 9],
...     ['Grumpy Cat', 'black and white', 1],
...     ['Nyan', 'Rainbow', '+Infinity'],
... ])

Tables generator must be built before being added to the story. There are 2
output of the table generator: :class:`reportlab.platypus.Table` and
:class:`reportlab.platypus.LongTable`. Long tables are more efficient with
tables containing a lot of data.

The method takes the style as the arguments and the options as keywords. A
:class:`reportlab.platypus.TableStyle` is automatically created with the
arguments. The styles can use the standard tuples as defined by :mod:`platypus`
or use the :data:`pdf_generator.table.styles` shortcut.

>>> from pdf_generator.table import styles
>>> s.append(table.get_long_table(
...     styles.first_row.LineBelow(0.5, colors.black),
...     styles.first_col.Alignment('LEFT'),
...     styles.Alignment((1, -1), (-1, -1), 'CENTER'),
...     colWidths=[None, 3 * units.cm, 2 * units.cm],
... ))


Images
------

PDF Generator helps with images. The :class:`pdf_generator.styles.Image` helps
by applying a target width or height to an image with a given ratio.

For example to include an image from PIL in the PDF at a height of 5 cm.

>>> import PIL.Image
>>> from pdf_generator.styles import Image
>>> image = PIL.Image.open('image.png')
>>> width, height = image.size
>>> img = Image(
...     image.filename,
...     height=5 * units.cm,
...     width / float(height),
... )
>>> s.append(img)

Importing HTML
--------------

PDF Generator includes a HTML transformer utility. The supported HTML tags are
a, center, blockquote, ul, li, br, and img. The function
:func:`pdf_generator.from_html.html_to_rlab` transforms a string of HTML to a
single table.

Medias included from **img** tags are located by the *medias locator*. Standard
medias locators are shipped in the module :mod:`pdf_generator.medias`. A media
locator is a callable that returns the whole path of the file when it's called
with the value of the **src** attribute of the img tag. The default medias
locator raise a :exc:`RuntimeError` when called.

Links are converted from the **href** attribute of *a* tags by the
**link_handler**. The link_handler may be ``None``, a string or a callable.
When the link_handler is not specified or is ``None``, the links are copied
without transformation. When it's a string, this string is joined with the href
by a ``/``. The join will avoid double or triple ``/``. When link_handler is a
callable, it must return the desired link target from the href.

Example: include the image and it caption. The image path is relative to
/var/www/static and the link will lead to http://example.com/img/image.png.

>>> from pdf_generator.from_html import html_to_rlab
>>> from pdf_generator.medias import PathMediasLocator
>>> html = '<a href="img/image.png"><img src="img/image_thumb.png" /></a><br />This image"
>>> flowable = html_to_rlab(html, PathMediasLocator('/var/www/static'),
...                         'http://example.com')
>>> s.append(flowable)

---------
Templates
---------

.. currentmodule:: pdf_generator.templates

For the more advanced needs, PDF generator includes a template engine. The
template engines uses the :class:`reportlab.platypus.Frame` and
:class:`reportlab.platypus.PageTemplate` to defines printable zones on a page.
The building of a template requires a
:class:`Template`. Pages containing frames are added to
this template by its method :meth:`Template.add_page`.

:meth:`~Template.add_page` requires a list of tuples of
length 4 defining the top left corner's position and the width and height. The
position is a tuple of 2 values, that are numbers, :class:`Fraction`, or a
combination of them. The numbers are absolute positions relative to the top
left corner of the page with the margin applied. The :class:`Fraction` are
relative to the printable width or height of the page, the margin excluded. The
width and height can be numbers, :class:`Fraction` or ``None``. Numbers are
exprimed as reportlab units, :class:`Fraction` are relative to the printable
width and height of the page and ``None`` indicates that the frame should take
all the space up to the bottom or right borders.

Numbers, :class:`Fraction` and ``None`` are mixable in each frame definition.

.. note::

    Frames definitions resolving outside of the page or in the margins are
    silently reduced to be contained in the page.


>>> from pdf_generator.templates import Template
>>> t = Template(pagesize=(29, 9), margins=[1, 7, 1, 1])
>>> t.add_page([
...     (0, 0, 1, 1),  # Frame A
...     (Fraction(0.5), 5, None, None),  # Frame B
... ])
>>> t('out.pdf', 'title', 'author', debug=True)

.. note:: Using debug

    When debug is True, outlines of the frames are highlighted in black.

Result::

    +------------------------+
    |                        |
    |  +-+-----------+       |
    |  |A|           |       |
    |  +-+           |       |
    |  |             |       |
    |  |      +------+       |
    |  |      |B     |       |
    |  +------+------+       |
    |                        |
    +------------------------+

Building row by row
-------------------

The template if often buildable row by row. PDF Generator includes a
:class:`TemplateRows` to build a page row by row. Each :class:`TemplateRows`
represents a page split in rows and each row is split in cell. The cells make
:class:`Frame`. Rows do not overlap and are adjacent. All the cells in a row
have the same height.

>>> from pdf_generator.templates import TemplateRows, Fraction
>>> tr = TemplateRows()

The rows are cut by calling :meth:`~TemplateRows.row` and
:meth:`~TemplateRows.skip`. They both take a number, a :class:`Fraction` or
``None``. A number is an absolute height in reportlab units, a :class:`Fraction`
is relative to the :attr:`Template.printable_height` and ``None`` means the
remaining of the page until the bottom. Numbers and :class:`Fraction` are not
mixable. ``None`` can only be used as the last call of the
:class:`TemplateRows` and is usable with numbers and fractions.

Each :meth:`~TemplateRows.row` call returns a :class:`TemplateRow`. The
:class:`TemplateRow` has two ways of splitting into cells. Those two ways are
exclusive, they cannot be used on the same :class:`TemplateRow`, but they can
be used on different rows of a :class:`TemplateRows`.

First, the split by :meth:`~TemplateRow.cell` and :meth:`TemplateRow.skip`
defines the zones that are frames and the one that are white space. They both
return the :class:`TemplateRow` object for easy chaining. They accept numbers
and :class:`Fraction` and ``None``. Just like the :class:`TemplateRows`,
numbers are absolute width, Fraction are relative to the
:attr:`Template.printable_width` and ``None`` means the rest of the row until
the left side.

>>> # Frames 1, 2 & 3
>>> tr.row(3 * units.cm).cell(2 * units.cm).skip(1 * units.cm).cell()
>>> # Frames 4
>>> tr.row(6 * units.cm).cell(5 * units.cm)

Result::

    +---+--+-+-----+
    | 1 | 2| |  3  |
    +---+--+-+-----+
    |      |       |
    |    4 |       |
    +------+-------+

Secondly, the :meth:`TemplateRow.split` method cut the row in a number of
frames. If only one number is given to split, the row is split in this number
of cells of equal sizes. If more than one is given, the row is divided in as
many cell as there are arguments and each cell has the ponderation of its
value.

>>> # Frames 1 & 2
>>> tr.cell(3 * units.cm).split(2)
>>> # Frames 3, 4, 5 & 6
>>> tr.cell(3 * units.cm).split(2, 2, 1, 3)

Result::

    +---------+---------+
    |    1    |   2     |
    +----+----+--+------+
    |  3 |  4 | 5|   6  |
    +----+----+--+------+


.. note:: The rest of the page

    To create a frame taking the rest of the page, just call :meth:`row` and
    :meth:`cell` without arguments.

    >>> tr.row().cell()


Navigating through frames
-------------------------

:class:`SimpleTemplate` is just like a :class:`Template` but has a single page
template with a single frame. :class:`Template` can have more than one page
template and each page can have more than one frame. When they are used with a
Story, they have an active page template and all the new pages added to the
document have this same page template.

.. currentmodule:: pdf_generator.pdf_generator

:class:`Story` proposes some methods to navigates between frames, pages and
templates. :meth:`Story.next_frame` ends the current frame and pass to the next
frame of the template. If it was the last frame of the template a new page is
added. :meth:`Story.next_page` ends the current page and start a new page.

:meth:`Story.next_template` does not ends anything. It tells the render engine
that the new page to be started will use another page template.

.. note:: Changing the frame.

    When a frame is filled, reportlab automatically switch to the next. If it
    was the last frame of the template, a new page **of the same page
    template** is added to the document.


For example, this report has a introduction page, a set of two column pages and
a conclustion page::

    Introduction                2 columns                   Conclusion
    +----+----+------+          +-------+--------+          +----------------+
    | F1 | F2 |  F3  |          |       |        |          |       F1       |
    +----+--+-+------+          |  F1   |   F2   |          +----------------+
    |   F4  |  F5    |          |       |        |          |       F2       |
    +-------+--------+          +-------+--------+          +----------------+

Creating the template
*********************

>>> from reportlab.lib import units
>>> from pdf_generator.templates import Template, TemplateRows, Fraction
>>> t = Template()
>>> intro = TemplateRows()
>>> intro.row(5 * units.cm).split(1, 1, 3)
>>> intro.row().split(2)
>>> t.add_page(intro)
>>> columns = TemplateRows()
>>> columns.row().split(2)
>>> t.add_page(columns)
>>> conclusion = TemplateRows()
>>> conclusion.row(Fraction(.75)).cell()
>>> conclusion.row().cell()
>>> t.add_page(conclusion)

Filling the story
*****************

>>> from reportlab.platypus import XBox
>>> from pdf_generator import Story, Paragraph
>>> s = Story(t)
>>> s.append(Paragraph('Enix', 'h1'))  # Intro F1
>>> s.next_frame()
>>> s.append(XBox(4.5 * units.cm, 4.5 * units.cm, 'Logo'))  # Intro F2
>>> s.next_frame()
>>> s.append(Paragraph('Quarterly Report', 'h2'))  # Intro F3
>>> s.append(Paragraph('Q3 2014', 'h3'))
>>> s.next_frame()
>>> s.next_template() # Next page will use 2 columns design. Still have F4 & F5 to fill
>>> for x in xrange(1000):  # Lots of data, starts new pages of 2 columns
...     s.append(Paragraph(unicode(x)))
>>> s.next_template() # Switch to the conclusion template
>>> s.next_page() # Terminates the 2 column page, whatever the column we're on
>>> s.append(Paragraph('See you next year'))
>>> s.next_frame()
>>> s.append(Paragraph('Contact enix@enix.org'))
>>> with open('q3.pdf', 'wb') as out:
...     s.build(out, 'Q3 2014', 'Enix', debug=True)


--------------
Page numbering
--------------

.. currentmodule:: pdf_generator.page_number

PDF Generator includes a page numbering tool for the generation of PDF. It uses
a :class:`NumberedCanvasFactory` to generate a :class:`NumberedCanvas` which is
a subclass of :class:`reportlab.pdfgen.canvas.Canvas`. It's usable whith
:class:`Template` and :class:`SimpleTemplate` and even with :mod:`reportlab`
standard :class:`BaseDocTemplate`.

:class:`NumberedCanvasFactory` take the position and the label. The position
are two number. The positive value of the position are relative to the top left
corner and the negative values are relative to the bottom right corner.

The label is either a callable or a string. If the label is a callable, it's
called with the current page (numbered from 1) and the total number of pages.
If it's a string, it is a format string with ``{}`` and gets the same arguments
as the callable. By default the string is ``{}/{}`` for example printing 1/2,
2/2 for a 2 pages document.

>>> story = Story(SimpleTemplate())
>>> for x in 'ABC':
...     s.append(Paragraph(x))
...     s.next_page()
>>> story.build(out,
...                  title=u'PDF with page number',
...                  author=u'Enix PDF Generator',
...                 canvasmaker=NumberedCanvasFactory(-1 * units.cm, 1.5 * units.cm,
...                 lambda x, y: 'last' if x == y else str(x),
...                 )

Result::

    +----------------+      +----------------+     +----------------+
    |A             1 |      |B             2 |     |C          last |
    |                |      |                |     |                |
    |                |      |                |     |                |
    |                |      |                |     |                |
    |                |      |                |     |                |
    |                |      |                |     |                |
    |                |      |                |     |                |
    +----------------+      +----------------+     +----------------+

-----------------
Header and footer
-----------------

.. currentmodule:: pdf_generator.templates

PDF Generator handles headers and footers. The :class:`Template` and the
:class:`SimpleTemplate` take a **header**, **footer** and **page_end**
arguments. **page_end** is a general purpose callback called on each page. See
the `Reportlab documentation`_ for more details on the usage of pageEnd.

When they are given header and footer must be :class:`Paragraph` instances.
Those paragraph are written in the margins (top for the header and bottom for
the footer). The paragraph is centered in the margin.

A line is drawn over the footer and under the header in the same color as the
paragraph.

>>> t = SimpleTemplate(margins=(50, 10),
...                    header=Paragraph('header'),
...                    footer=Paragraph('footer'),
...                    )
>>> s = Story(t)

Result::

    +-------------+
    |   header    |
    | ----------- |
    |             |
    |             |
    |             |
    | ----------- |
    |    footer   |
    +-------------+
