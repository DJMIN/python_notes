# -*- coding: utf-8 -*-
"""callable signatures"""

import collections
import functools
import inspect

# inspect.signature can extract signature of input callable object
# here follows some tools based on signatures


def function_parameter(func, *args, **kwargs):
    """extract function parameters in ordered dict"""
    # make result container (keep param order)
    func_param = collections.OrderedDict()
    # make signature and extract param part
    sig_param = inspect.signature(func).parameters
    # loop param and keep index, which can be used to parse args
    for idx, param in enumerate(sig_param.values()):
        # if param not in args or kwargs, use default value
        val = args[idx] if idx < len(args) else \
            kwargs.get(param.name, param.default)
        # save value to result container
        func_param[param.name] = val
    # return result to function caller
    return func_param

# this 'function_parameter' can be used in decorator


# first define a function to convert param dict to string
def calling_description(func, *args, **kwargs):
    """return a string including function name and parameter values"""
    param = function_parameter(func, *args, **kwargs)
    param_lst = [f"{k}={repr(v)}" for k, v in param.items()]
    param_str = ', '.join(param_lst)
    return f"{func.__name__}({param_str})"


# then, define the target decorator
def print_detail(func):
    """decorator to print details of on-called function"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        info = calling_description(func, *args, **kwargs)
        print(f"calling {info}")
        return func(*args, **kwargs)
    return wrapper


# try decorating a function and see the output
@print_detail
def add_triple_integer(a, b=1, c=1):
    return a + b + c


add_triple_integer(3, b=2)
# output: calling add_triple_integer(a=3, b=2, c=1)
