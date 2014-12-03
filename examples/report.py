#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Multipage report with header, footer, and pages numbers
"""

from reportlab.lib import units, colors, enums
from reportlab.platypus import XBox

from pdf_generator import Story, Paragraph
from pdf_generator.page_number import NumberedCanvasFactory
from pdf_generator.templates import Template, TemplateRows, Fraction

t = Template(margins=(50, 10),
             header=Paragraph('header header header',
                              textColor=colors.red,
                              fontSize=8,
                              alignment=enums.TA_CENTER,
                              ),
             footer=Paragraph('footer footer footer',
                              textColor=colors.blue,
                              fontSize=8,
                              alignment=enums.TA_CENTER,
                              ),
             )

intro = TemplateRows()
intro.row(5 * units.cm).split(1, 2, 2)
intro.row().split(2)
t.add_page(intro)

columns = TemplateRows()
columns.row().split(2)
t.add_page(columns)

conclusion = TemplateRows()
conclusion.row(Fraction(.75)).cell()
conclusion.row().cell()
t.add_page(conclusion)

s = Story(t)
s.append(Paragraph('Enix', 'h1'))  # Intro F1
s.next_frame()
s.append(XBox(4.5 * units.cm, 4.5 * units.cm, 'Logo'))  # Intro F2
s.next_frame()
s.append(Paragraph('Quarterly Report', 'h2'))
s.append(Paragraph('Q3 2014', 'h3'))
s.next_frame()

# Next page will use 2 columns design. Still have F4 & F5 to fill
s.next_template()

for x in xrange(400):  # Lots of data
    s.append(Paragraph(unicode(x)))

s.next_template()  # Switch to the conclusion template
s.next_page()  # Terminates the 2 column page, wathever the frame were on

s.append(Paragraph('See you next quarter'))
s.next_frame()

s.append(Paragraph('Contact: enix@enix.org'))

with open('q3.pdf', 'wb') as out:
    s.build(out, 'Q3 2014', 'PDF Generator',
            canvasmaker=NumberedCanvasFactory(- 1 * units.cm, 1 * units.cm))


print 'PDF q3.pdf created'
