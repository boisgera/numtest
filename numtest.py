#!/usr/bin/env python
# coding: utf-8

# Python 2.7 Standard Library
import doctest
import re
import sys

# Third-Party Libraries
import numpy


__author__ = u"Sébastien Boisgérault <Sebastien.Boisgerault@mines-paristech.fr>"
__version__ = "1.0.0"
__license__ = "MIT License"


_doctest_OutputChecker = doctest.OutputChecker

_float = r"""[-+]?
             (?: 
                 (?:\d*\.(?P<digits>\d+)) 
                 | 
                 (?:\d+\.?) 
             )
             (?:[Ee](?P<exponent>[+-]?\d+))?
          """
_float = re.compile(_float, re.VERBOSE)

def exponent(number):
    match = _float.match(number)
    if not match or match.group() != number:
        raise ValueError("invalid float syntax {0!r}".format(number))
    else:
        ndigits  = len(match.group("digits") or "")
        exponent = int(match.group("exponent") or 0)
        return exponent - ndigits

NUMBER = doctest.register_optionflag("NUMBER")
doctest.NUMBER = NUMBER
doctest.__all__.append("NUMBER")
doctest.COMPARISON_FLAGS = doctest.COMPARISON_FLAGS | NUMBER

def number_match(want, got):
    threshold = 0.5 * 10 ** (exponent(want))
    match = abs(float(want) - float(got)) < threshold    
    if not match:
        raise RuntimeError(want, got)
    else:
        return True    

def array_match(want, got):
    try: 
        want_array = eval_array(want)
        got_array = eval_array(got)
    except SyntaxError:
        return False
    if numpy.shape(want_array) != numpy.shape(got_array):
        return False
    else:
        want_array = numpy.ravel(want_array)
        got_array = numpy.ravel(got_array)
        indices = range(len(want_array))
        return all(number_match(want_array[i], got_array[i]) for i in indices)

def eval_array(numbers):
    """
Read a scalar or array of numbers representation as an array of strings:

    >>> print eval_array("1.34e-7")
    1.34e-7
    >>> print eval_array("42")
    42
    >>> print eval_array("[42]")
    ['42']
    >>> print eval_array("[1, 2, 3]")
    ['1' '2' '3']
    >>> print eval_array("[[0.1, 2.00], [1e-2, 3.14], [6.78e7, 0.001e-6]]")
    [['0.1' '2.00']
     ['1e-2' '3.14']
     ['6.78e7' '0.001e-6']]
    """
    _numbers = eval(numbers) # ouch.
    shape = numpy.shape(_numbers)
    if not shape:
        return numpy.array(numbers)
    else:
        numbers = [m.group(0) for m in re.finditer(_float, numbers)]
        return numpy.reshape(numbers, shape)

class NumTestOutputChecker(_doctest_OutputChecker):
    def check_output(self, want, got, optionflags):
        if optionflags & NUMBER:
            if want.endswith("\n"):
                want = want[:-1]
            if got.endswith("\n"):
                got = got[:-1]
            return array_match(want, got)
        else:
            super_check_output = _doctest_OutputChecker.check_output
            return super_check_output(self, want, got, optionflags)
    def output_difference(self, example, got, optionflags):
        super_output_difference = _doctest_OutputChecker.output_difference
        return super_output_difference(self, example, got, optionflags)

doctest.OutputChecker = NumTestOutputChecker

def test():
    """
Test the succes of doctest monkey-patching

    >>> import doctest
    >>> doctest.OutputChecker == NumTestOutputChecker
    True
    >>> _ = doctest.NUMBER
    >>> from doctest import *
    >>> NUMBER == doctest.NUMBER
    True
    >>> OutputChecker == NumTestOutputChecker
    True

Test the directive on scalars:

    >>> import math
    >>> math.pi
    3.141592653589793
    >>> math.pi
    3.141592653589793
    >>> math.pi # doctest: +NUMBER
    3.141592653589793
    >>> math.pi # doctest: +NUMBER
    3.1416
    >>> math.pi # doctest: +NUMBER
    3.14
    >>> math.pi # doctest: +NUMBER
    3
    >>> 951 # doctest: +NUMBER
    1e3
    >>> 1049 # doctest: +NUMBER
    1e3

Test the directive on arrays:

    >>> [3.1415, 0.097, 13.1, 7, 8.22222e5, 0.598e-2] # doctest: +NUMBER
    [3.14, 0.1, 13, 7, 8.22e5, 6.0e-3]
    >>> [[0.333, 0.667], [0.999, 1.333]] # doctest: +NUMBER
    [[0.33, 0.667], [0.999, 1.333]]
    >>> [[[0.101]]] # doctest: +NUMBER
    [[[0.1]]]
    """
    doctest.testmod()

if __name__ == "__main__":
    test()

