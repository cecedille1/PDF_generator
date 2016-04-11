#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from paver.easy import task

try:
    import sett  # noqa
except ImportError:
    pass


def find_version(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath, 'r') as init:
        for line in init:
            if line.startswith('__version__'):
                x, version = line.split('=', 1)
                return version.strip().strip('\'"')
        else:
            raise ValueError('Cannot find the version in {0}'.format(filename))


def parse_requirements(requirements_txt):
    requirements = []
    try:
        with open(requirements_txt, 'r') as f:
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


@task
def setup_options():
    from paver.setuputils import setup

    with open('README.rst') as reame_rst:
        readme = reame_rst.read()

    setup(
        name='pdf_generator',
        version=find_version('pdf_generator/__init__.py'),
        description='PDF Generation utils',
        long_description=readme,
        author=u'Grégoire ROCHER',
        author_email='gr@enix.org',
        packages=[
            'pdf_generator',
        ],
        include_package_data=True,
        install_requires=parse_requirements('requirements.txt'),
        zip_safe=False,
        keywords='pdf_generator',
        classifiers=[
        ],
        test_suite='tests',
    )
