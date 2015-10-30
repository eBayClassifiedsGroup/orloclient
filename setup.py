#!/usr/bin/env python
from __future__ import print_function

__author__ = 'alforbes'

# from distutils.core import setup
from setuptools import setup, find_packages
import multiprocessing  # nopep8

setup(
    name='orloclient',
    version='0.0.1',
    description='Client to the Orlo deployment data capture API',
    author='Alex Forbes',
    author_email='alforbes@ebay.com',
    license='GPL',
    long_description=open('README.md').read(),
    url='https://github.com/eBayClassifiedsGroup/orloclient',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
      'requests',
    ],
    tests_require=[
      'Flask-Testing',
      'orlo',
    ],
    test_suite='tests',
)
