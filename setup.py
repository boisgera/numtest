#!/usr/bin/env python
# coding: utf-8

import numtest
from distutils.core import setup

setup(name="numtest",
      version=numtest.__version__,
      description="doctest extension to compare floating-point numbers",
      author=u"Sébastien Boisgérault",
      url="https://github.com/boisgera/numtest",
      py_modules=["numtest"],
     )

