#!/usr/bin/env python
# coding: utf-8

import numtest
from distutils.core import setup

setup(name="numtest",
      version=numtest.__version__,
      description="doctest extension to compare floating-point numbers",
      author=u"Sébastien Boisgérault",
      author_email="Sebastien.Boisgerault@mines-paristech.fr",
      url="https://github.com/boisgera/numtest",
      license="MIT License", 
      py_modules=["numtest"],
     )

