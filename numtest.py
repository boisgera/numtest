
import doctest

_doctest_OutputChecker = doctest.OutputChecker

class NumTestOutputChecker(_doctest_OutputChecker):
    def check_output(self, want, got, optionflags):
        super_check_output = _doctest_OutputChecker.check_output
        return super_check_output(self, want, got, optionflags)
    def output_difference(self, example, got, optionflags):
        super_output_difference = _doctest_OutputChecker.output_difference
        return super_output_difference(self, example, got, optionflags)

doctest.OutputChecker = NumTestOutputChecker

NUMBER = doctest.register_optionflag("NUMBER")
doctest.NUMBER = NUMBER
doctest.__all__.append("NUMBER")

def test():
    """
    >>> import doctest
    >>> doctest.OutputChecker == NumTestOutputChecker
    True
    >>> _ = doctest.NUMBER
    >>> from doctest import *
    >>> NUMBER == doctest.NUMBER
    True
    >>> OutputChecker == NumTestOutputChecker
    True
    """
    doctest.testmod()

if __name__ == "__main__":
    test()

