from .base import input_meth_factory


import re


def float_pre_return(ret_val):
    print('\n', flush=True)
    ret_val = float(ret_val.replace(',', ''))
    return ret_val


def int_pre_return(ret_val):
    print('\n', flush=True)
    ret_val = int(ret_val.replace(',', ''))
    return ret_val


INT_RE = re.compile(r"^[0-9]{1,3}(,?[0-9]{3})*$")
int_input = input_meth_factory(INT_RE, pre_return=int_pre_return)


FLOAT_RE = re.compile(r"^[0-9]{1,3}(,?[0-9]{3})*(\.[0-9]+)?$")
float_input = input_meth_factory(FLOAT_RE, pre_return=float_pre_return)


MONEY_RE = re.compile(r"^\$?[0-9]{1,3}(,?[0-9]{3})*(\.[0-9]+)?$")
money_input = input_meth_factory(MONEY_RE, pre_return=float_pre_return)