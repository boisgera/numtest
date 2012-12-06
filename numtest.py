
import doctest

class NumTestOutputChecker(doctest.OutputChecker):
    def check_output(self, want, got, optionflags):
        super_check_output = super(NumTestOutputChecker, self).check_output
        return super_check_output(self, want, got, optionflags)
    def output_difference(self, example, got, optionflags):
        super_output_difference = super(NumTestOutputChecker, self).output_difference
        return super_output_difference(self, example, got, optionflags)

doctest.OutputChecker = NumTestOutputChecker
