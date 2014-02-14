#!/usr/bin/env python
# coding: utf-8
"""
Doctest extension to compare floating-point numbers
"""

# Python 2.7 Standard Library
import doctest
import re
import sys
import StringIO
import tokenize

# Third-Party Libraries
import numpy

#
# Metadata
# ------------------------------------------------------------------------------
#
from about_numtest import *

#
# ------------------------------------------------------------------------------
#

_doctest_OutputChecker = doctest.OutputChecker

_float = r"""[-+]?
             (?: 
                 (?:\d*\.(?P<digits>\d+)) 
                 | 
                 (?:\d+\.?) 
             )
             (?:[Ee](?P<exponent>[+-]?\d+))?
          """
_float_pattern = re.compile(_float, re.VERBOSE)

def exponent(number):
    match = _float_pattern.match(number)
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
        want_array = parse_numbers(want)
        got_array  = parse_numbers(got)
    except SyntaxError:
        return False
    if numpy.shape(want_array) != numpy.shape(got_array):
        return False
    else:
        want_array = numpy.ravel(want_array)
        got_array = numpy.ravel(got_array)
        indices = range(len(want_array))
        return all(number_match(want_array[i], got_array[i]) for i in indices)

def parse_numbers(text):
    """
Parse text that represent numbers.

The text can be a single number or a list of numbers that may be nested.

    >>> parse_numbers("1.34e-7")
    '1.34e-7'
    >>> parse_numbers("42")
    '42'
    >>> parse_numbers("[42]")
    ['42']
    >>> parse_numbers("[1, 2, 3]")
    ['1', '2', '3']
    >>> parse_numbers("[[0.1, 2.00], [1e-2, 3.14], [6.78e7, 0.001e-6]]")
    [['0.1', '2.00'], ['1e-2', '3.14'], ['6.78e7', '0.001e-6']]
    >>> parse_numbers("array([0, 1, 2], uint8)")
    ['0', '1', '2']
    >>> parse_numbers("-1.0")
    '-1.0'
    """
    text_wrapper = StringIO.StringIO(text).readline
    tokens = list(tokenize.generate_tokens(text_wrapper))

    def valid(token):
        type_, text, _, _, _ = token
        if type_ in [tokenize.NUMBER, tokenize.NL, tokenize.ENDMARKER]:
            return True
        elif type_ == tokenize.OP and text in ["[", "]", ",", "+", "-"]:
            return True
        else:
            return False

    while tokens and not valid(tokens[0]):
        tokens.pop(0)
    if not tokens:
        return None

    stack = [[]]
    fold = lambda: stack[-2].append(stack.pop())
    insert = lambda: stack.append([])
    push = lambda item: stack[-1].append(item)

    sign = ""
    for token in tokens:
        type_, text, _, _, _ = token
        if type_ == tokenize.OP:
            if text == "[":
                insert()        
            elif text == "]":
                fold()
            elif text == ",":
                pass
            elif text == "-":
                sign = "-"
            elif text == "+":
                pass
            else:
                break
        elif type_ == tokenize.NUMBER:
            text = sign + text
            push(text)
            sign = ""
        elif type_ == tokenize.NL:
            pass
        else:
            break

    if len(stack) != 1:
        raise SyntaxError("invalid syntax {0!r}".format(text))
    else:
        return stack[0][0]

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

Test the directive on lists:

    >>> [3.1415, 0.097, 13.1, 7, 8.22222e5, 0.598e-2] # doctest: +NUMBER
    [3.14, 0.1, 13, 7, 8.22e5, 6.0e-3]
    >>> [[0.333, 0.667], [0.999, 1.333]] # doctest: +NUMBER
    [[0.33, 0.667], [0.999, 1.333]]
    >>> [[[0.101]]] # doctest: +NUMBER
    [[[0.1]]]

Test the directive on arrays:

    >>> from numpy import array
    >>> array([]) # doctest: +NUMBER
    []
    >>> array([1.0]) # doctest: +NUMBER
    [1]
    >>> array([-1.0]) # doctest: +NUMBER
    [-1.0]
    >>> array([-1.0, 1.0, -1.0, 1.0]) # doctest: +NUMBER
    [-1.0, 1.0, -1.0, 1.0]
    >>> array([[1.0, 2.0], [3.0, 4.0]]) # doctest: +NUMBER
    [[1, 2], [3, 4]]
    """
    doctest.testmod()

if __name__ == "__main__":
    test()

