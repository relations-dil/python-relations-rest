#!/usr/bin/env python

from setuptools import setup

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setup(
    name="relations-rest",
    version="0.3.0",
    package_dir = {'': 'lib'},
    py_modules = [
        'relations_rest',
        'relations_rest.source',
        'relations_rest.unittest'
    ],
    install_requires=[
        'requests==2.25.1',
        'relations-restx==0.6.1'
    ],
    url="https://github.com/relations-dil/python-relations-rest",
    author="Gaffer Fitch",
    author_email="relations@gaf3.com",
    description="API Modeling through REST",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license_files=('LICENSE.txt',),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ]
)
