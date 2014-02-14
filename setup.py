#!/usr/bin/env python
# coding: utf-8

# Python 2.7 Standard Library
import os
import sys

# Third-Party Libraries
import about
import setuptools


contents = dict(py_modules=["numtest", "about_numtest"])
metadata = about.get_metadata("about_numtest")
requirements = dict(install_requires="numpy")

info = {}
info.update(contents)
info.update(metadata)
info.update(requirements)

if __name__ == "__main__":
    setuptools.setup(**info)

