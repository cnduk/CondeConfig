# -*- coding: utf8 -*-

from os import path
from setuptools import setup, find_packages

DIRNAME = path.dirname(__file__)

setup(
    name='CondeConfig',
    version='0.0.1',
    packages=find_packages(),
    long_description=open(path.join(DIRNAME, 'README.md')).read(),
    install_requires=[
        'six',
    ],
    dependency_links=[],
    zip_safe=False
)
