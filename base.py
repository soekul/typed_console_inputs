__author__ = 'Luke Stamm - soekul@soekul.com'


import sys


class _Getch:
    """
    Gets a single character from standard input.
    Does not echo to the screen.
    """
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getch = _Getch()


def input_meth_factory(re_eval, pre_return=None):
    def ret_func(prompt_val):
        # echo the prompt before reading input
        print(prompt_val, end='', flush=True)
        line_val = prompt_val
        ret_val = ""

        # break on enter, bail on ctrl+c/d
        while True:
            c = getch()

            if ord(c) == 13:  # carriage return
                #  User has pressed enter, check current ret_val against
                #  regular expression
                match = re_eval.fullmatch(ret_val)
                if match is not None:
                    break
                else:
                    print("\nInvalid input, try again.")
                    print(prompt_val, ret_val, end='', flush=True)

            elif ord(c) in [3, 4]:  # ctrl+c and ctrl+d
                #  Exit if ctrl+c/d are pressed
                sys.exit(-1)

            elif ord(c) in [8, 127]:  # backspace, delete
                #  Handle backspace/delete by starting with a carriage return
                #  then writing spaces and ending with anther carriage return
                #  before writing the prompt and return value again
                num_spaces = len(ret_val) + len(prompt_val) + 3
                print('\r', " " * num_spaces, end='\r', flush=True)
                if len(ret_val) > 0:
                    ret_val = ret_val[:-1]
                print(prompt_val, ret_val, end='', flush=True)

            else:  # all other character
                if 32 <= ord(c) <= 125:  # only printable characters
                    ret_val += c
                num_spaces = len(ret_val) + len(prompt_val) + 1
                print(" " * num_spaces, end='\r', flush=True)
                print(prompt_val, ret_val, end='', flush=True)

        if pre_return is not None and callable(pre_return):
            ret_val = pre_return(ret_val)
        return ret_val

    return ret_func
