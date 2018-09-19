from .base import RegExInputValidatorMethod


import re


INT_RE = re.compile(r"^[0-9]{1,3}(,?[0-9]{3})*$")
FLOAT_RE = re.compile(r"^[0-9]{1,3}(,?[0-9]{3})*(\.[0-9]+)?$")
MONEY_RE = re.compile(r"^\$?[0-9]{1,3}(,?[0-9]{3})*(\.[0-9]+)?$")


class CommaDelimitedNumericBase(RegExInputValidatorMethod):
    def __call__(self, *args, **kwargs):
        ret_val = super(CommaDelimitedNumericBase, self)\
            .__call__(*args, **kwargs)
        return ret_val.replace(",", '')  # remove commas before casting


class IntInputMethod(CommaDelimitedNumericBase):
    def __call__(self, *args, **kwargs):
        ret_val = super(IntInputMethod, self).__call__(*args, **kwargs)
        return int(ret_val)


class FloatInputMethod(CommaDelimitedNumericBase):
    def __call__(self, *args, **kwargs):
        ret_val = super(FloatInputMethod, self).__call__(*args, **kwargs)
        return float(ret_val)


int_input = IntInputMethod(INT_RE)
float_input = FloatInputMethod(FLOAT_RE)
money_input = FloatInputMethod(MONEY_RE)
