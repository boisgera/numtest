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
from .about_numtest import *

#
# ------------------------------------------------------------------------------
#

# declare the new doctest directive NUMBER 
NUMBER = doctest.register_optionflag("NUMBER")
doctest.NUMBER = NUMBER
doctest.__all__.append("NUMBER")
doctest.COMPARISON_FLAGS = doctest.COMPARISON_FLAGS | NUMBER



# TODO: need to handle inf / nan at the regular expression level ...
#       at least for the single top-level capture version.

# TODO: best strategy wrt integers ? capture or not ?

# number pattern
_number = re.compile(r"""
(?P<number>
  (?P<mantissa>
    (?:
      (?:
        (?P<integer1> [+-]?\d*)\.(?P<fraction>\d+) 
      )
      | 
      (?:
        (?P<integer2> [+-]?\d+)\.?
      ) 
    )
  )
  (?:
    [Ee]
    (?P<exponent>[+-]?\d+)
  )?
)
""", re.VERBOSE)

# same thing, but with a single top-level capture
_number_alt = re.compile(r"""
(
  (?:
    [+-]?
    (?:
      (?: \d*\.\d+) | (?: \d+\.?) 
    )
  )
  (?: [Ee][+-]?\d+)?
)
""", re.VERBOSE)

def anatomy(number):
    match = _number.match(number)
    if not match or match.group() != number:
        raise ValueError("invalid number syntax {0!r}".format(number))
    dct = match.groupdict()
    integer = 0
    for key in ["integer1", "integer2"]:
        if dct[key] is not None:
            integer = int(dct[key] or "0")
    fraction = [int(digit) for digit in (dct["fraction"] or "")]
    exponent = int(dct["exponent"] or "0")
    return integer, fraction, exponent



def number_match(want, got):
    if want == "nan":
       return got == "nan""
    elif want in ["inf", "-inf"]:
        return got == want or (got == "+inf" and want == "inf")
    else:
        iw, fw, ew = anatomy(want)
        while fw:
            iw = 10 * iw + fw.pop(0)
            ew = ew - 1
        ig, fg, eg = anatomy(got)
        while eg > ew:
            if fg:
                new_digit = fg.pop(0)
            else:
                new_digit = 0
            ig = 10 * ig + new_digit
            eg = eg - 1
        while eg < ew:
            new_digit = ig % 10
            ig = ig // 10
            fg.insert(0, new_digit)
            eg = eg + 1
        half = [5]
        if fg == []:
            fg = [0]
        elif len(fg) > 1:
            half.extend((len(fg) - 1) * [0])

    print iw, fw, ew
    print ig, fg, eg

    if ig == iw and fg <= half:
        return True
    elif ig == iw - 1 and fg >= half:
        return True
    else:
        return False
            

 

def exponent(number):
    match = _float_pattern.match(number)
    if not match or match.group() != number:
        raise ValueError("invalid float syntax {0!r}".format(number))
    else:
        ndigits  = len(match.group("digits") or "")
        exponent = int(match.group("exponent") or 0)
        return exponent - ndigits

def _number_match(want, got):
    if want in ["inf", "-inf"]:
        return got == want or (got == "+inf" and want == "inf")
    else:
        threshold = 0.5 * 10 ** (exponent(want))
        return abs(float(want) - float(got)) <= threshold    

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
    >>> parse_numbers("inf")
    'inf'
    """
    text_wrapper = StringIO.StringIO(text).readline
    tokens = list(tokenize.generate_tokens(text_wrapper))

    def valid(token):
        type_, text, _, _, _ = token
        if type_ in [tokenize.NUMBER, tokenize.NL, tokenize.ENDMARKER]:
            return True
        elif type_ == tokenize.NAME and text == "inf":
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
        elif type_ == tokenize.NAME and text == "inf":
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

#
# Numerical Output Checker
# ------------------------------------------------------------------------------
#
_doctest_OutputChecker = doctest.OutputChecker

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

# monkey-patching
doctest.OutputChecker = NumTestOutputChecker

#
# Unit Tests
# ------------------------------------------------------------------------------
#
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
    >>> 1e500 # doctest: +NUMBER
    inf

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

