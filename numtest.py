
import __builtin__
import doctest
import re
import sys

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

def exponent(number_repr):
    match = _float.match(number_repr)
    if not match or match.group() != number_repr:
        raise ValueError("invalid float syntax {0!r}".format(number_repr))
    else:
        ndigits  = len(match.group("digits") or "")
        exponent = int(match.group("exponent") or 0)
        return exponent - ndigits

NUMBER = doctest.register_optionflag("NUMBER")
doctest.NUMBER = NUMBER
doctest.__all__.append("NUMBER")
doctest.COMPARISON_FLAGS = doctest.COMPARISON_FLAGS | NUMBER

def number_match(target, candidate):
    threshold = 0.5 * 10 ** (exponent(target))
    return abs(float(target) - float(candidate)) < threshold    
    
class NumTestOutputChecker(_doctest_OutputChecker):
    def check_output(self, want, got, optionflags):
        if optionflags & NUMBER:
            try:
                target, candidate = want[:-1], got[:-1]
                return number_match(target, candidate)
            except ValueError:
                print "****"
                return False
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

Test the directive:
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
    """
    doctest.testmod()

if __name__ == "__main__":
    test()

