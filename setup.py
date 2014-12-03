#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


from setuptools import setup

readme = open('README.rst').read()


def find_version(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath) as init:
        for line in init:
            if line.startswith('__version__'):
                x, version = line.split('=', 1)
                return version.strip().strip('\'"')
        else:
            raise ValueError('Cannot find the version in {0}'.format(filename))


def parse_requirements(requirements_txt):
    requirements = []
    try:
        with open(requirements_txt, 'rb') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue
                if line.startswith('-'):
                    raise ValueError('Unexpected command {0} in {1}'.format(
                        line,
                        requirements_txt,
                    ))

                requirements.append(line)
        return requirements
    except IOError:
        return []


build_info = dict(
    name='pdf_generator',
    version=find_version('pdf_generator/__init__.py'),
    description='PDF Generation utils',
    long_description=readme,
    author=u'Grégoire ROCHER',
    author_email='gr@enix.org',
    packages=[
        'pdf_generator',
    ],
    package_dir={
        'pdf_generator': 'pdf_generator'
    },
    include_package_data=True,
    install_requires=parse_requirements('requirements.txt'),
    zip_safe=False,
    keywords='pdf_generator',
    classifiers=[
    ],
    test_suite='tests',
)

if __name__ == '__main__':
    setup(**build_info)
