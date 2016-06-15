#!/usr/bin/env python
# coding: utf-8

# Python 2.7 Standard Library
import os
import sys

# Pip Package Manager
try:
    import pip
    import setuptools
    import pkg_resources
except ImportError:
    error = "pip is not installed, refer to <{url}> for instructions."
    raise ImportError(error.format(url="http://pip.readthedocs.org"))

def srcdir(path):
    return os.path.join(os.path.dirname(__file__), path)

# Extra Third-Party Libraries
sys.path.insert(1, srcdir(".lib"))
try:
    setup_requires = ["about>=4.0.0"]
    require = lambda *r: pkg_resources.WorkingSet().require(*r)
    require(setup_requires)
    import about
except pkg_resources.DistributionNotFound:
    error = """{req!r} not found; install it locally with:

    pip install --target=.lib --ignore-installed {req}
"""
    raise ImportError(error.format(req=" ".join(setup_requires)))
import about

# This Package
sys.path.insert(1, srcdir("numtest"))
import about_numtest

info = dict(
  metadata     = about.get_metadata(about_numtest),
  code         = dict(packages=setuptools.find_packages()),
  data         = {},
  requirements = dict(install_requires=["numpy"]),
  scripts      = {},
  plugins      = {},
  tests        = dict(test_suite="test.suite"),
)

if __name__ == "__main__":
    kwargs = {k:v for dct in info.values() for (k,v) in dct.items()}
    setuptools.setup(**kwargs)

