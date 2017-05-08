#!/usr/bin/env python
from __future__ import print_function
import os

__author__ = 'alforbes'

# from distutils.core import setup
from setuptools import setup, find_packages
import multiprocessing  # nopep8

tests_require=[
    'Flask-Testing',
    'httpretty',
    'orlo >= 0.4.0',
    'pytest',
    'mock',
]
install_requires = [
    'arrow',
    'requests',
]


setup(
    name='orloclient',
    version='0.4.2',
    description='Client to the Orlo deployment _data capture API',
    author='Alex Forbes',
    author_email='alforbes@ebay.com',
    license='GPL',
    long_description=open(os.path.join(os.getcwd(), 'README.md')).read(),
    url='https://github.com/eBayClassifiedsGroup/orloclient',
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    extras_require={'test': tests_require,
                    'install': install_requires},
    tests_require=tests_require,
    entry_points={
        'console_scripts': [
            'orloclient=orloclient.__main__:main'
        ]
    },
)
