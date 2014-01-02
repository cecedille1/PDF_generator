#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

readme = open('README.rst').read()

setup(
    name='pdf_generator',
    version='0.1.1',
    description='PDF Generator',
    long_description=readme,
    author='Grégoire ROCHER',
    author_email='gr@enix.org',
    packages=[
        'pdf_generator',
    ],
    package_dir={
        'pdf_generator': 'pdf_generator'
    },
    include_package_data=True,
    install_requires=[
        'reportlab',
    ],
    zip_safe=False,
    keywords='pdf_generator',
    classifiers=[
    ],
    test_suite='tests',
)
