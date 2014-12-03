#!/usr/bin/env python
# -*- coding: utf-8 -*-


from pdf_generator import Story, Paragraph, SimpleTemplate


t = SimpleTemplate()
s = Story(t)

s.append(Paragraph('Title', 'h1'))
s.append(Paragraph('Subtitle', 'h2'))
s.append(Paragraph('''Ideo urbs venerabilis post superbas efferatarum gentium
cervices oppressas latasque leges fundamenta libertatis et
retinacula sempiterna velut frugi parens et prudens et dives
Caesaribus tamquam liberis suis regenda patrimonii iura
permisit.'''))


with open('basic.pdf', 'wb') as out:
    s.build(out, 'Basic', 'PDF Generator')

print 'PDF basic.pdf created'
