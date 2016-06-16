#!/usr/bin/env python
from __future__ import print_function
import os

__author__ = 'alforbes'

# from distutils.core import setup
from setuptools import setup, find_packages
import multiprocessing  # nopep8

setup(
    name='orloclient',
    version='0.2.0',
    description='Client to the Orlo deployment _data capture API',
    author='Alex Forbes',
    author_email='alforbes@ebay.com',
    license='GPL',
    long_description=open(os.path.join(os.getcwd(), 'README.md')).read(),
    url='https://github.com/eBayClassifiedsGroup/orloclient',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'arrow',
        'requests',
    ],
    tests_require=[
        'Flask-Testing',
        'httpretty',
        'orlo >= 0.2.0rc3',
    ],
    test_suite='tests',
)
