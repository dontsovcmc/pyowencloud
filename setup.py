#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Клиент к REST API облака api.owencloud.ru
"""
from __future__ import print_function
from setuptools import setup

VERSION_MAJOR = 0
VERSION_MINOR = 1

ver = '%d.%d' % (VERSION_MAJOR, VERSION_MINOR)

if __name__ == '__main__':
    """
    Создание пакета

    python setup.py sdist --formats=zip bdist_wheel   # или --formats=gztar
    twine upload dist/*
    """
    with open('README.md', 'r') as fh:
        long_description = fh.read()

    setup(
        name='pyowencloud',
        version=ver,
        description=__doc__.replace('\n', '').strip(),
        long_description=long_description,
        author='Dontsov E.',
        author_email='dontsovcmc@gmail.com',
        url='https://github.com/dontsovcmc/pyowencloud',
        py_modules=['pyowencloud'],
        include_package_data=True,
        packages=[
            'pyowencloud',
            'pyowencloud.examples'
        ],
        classifiers=(
            "Programming Language :: Python :: 2.7",
            'Programming Language :: Python :: 3',
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ),
        license='lgpl-3.0',
        platforms=['linux2', 'win32'],
        install_requires=[
            'requests>=2.19.1'
        ],
    )
