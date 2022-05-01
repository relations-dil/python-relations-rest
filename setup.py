#!/usr/bin/env python

from setuptools import setup, find_packages
setup(
    name="python-relations-rest",
    version="0.2.0",
    package_dir = {'': 'lib'},
    py_modules = [
        'relations_rest',
        'relations_rest.source',
        'relations_rest.unittest'
    ],
    install_requires=[
        'requests==2.25.1'
    ]
)
