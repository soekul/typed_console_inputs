__author__ = 'Luke Stamm - soekul@soekul.com'


import re


class _Getch(object):
    """
    Gets a single character from standard input.
    Does not echo to the screen.
    """
    def __init__(self, *args, **kwargs):
        super(_Getch, self).__init__(*args, **kwargs)
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix(object):
    def __init__(self, *args, **kwargs):
        super(_GetchUnix, self).__init__(*args, **kwargs)
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


class _GetchWindows(object):
    def __init__(self, *args, **kwargs):
        super(_GetchWindows, self).__init__(*args, **kwargs)
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getch = _Getch()


class RegExInputValidatorMethod(object):
    re_eval = re.compile(r"^.*$")

    def __init__(self, re_eval=None, *args, **kwargs):
        """
        Creates a callable object that processes input against a regular
        expression.
        :param re_eval:
        :param args:
        :param kwargs:
        """
        super(RegExInputValidatorMethod, self).__init__(*args, **kwargs)
        if re_eval is not None:
            self.re_eval = re_eval
        self.match = None

    def clear_line(self, prompt_value, value, end='\r'):
        """
        Clear the line by starting with a carriage return then overwrite
        the line with spaces and end with carriage return
        :param prompt_value:
        :param value:
        :param end:
        :return:
        """
        num_spaces = len(prompt_value) + len(value)
        print('\r', " " * num_spaces, end=end, flush=True)

    def print_line(self, prompt_value, value, end=''):
        """
        Echoes the current line in its entirety
        :param prompt_value:
        :param value:
        :param end:
        :return:
        """
        print(prompt_value, value, end=end, flush=True)

    def evaluate_failed(self, prompt_value, value):
        """
        Provides feedback when input does not validate against the regular
        expression
        :param prompt_value:
        :param value:
        :return:
        """
        print("\nInvalid input, try again.")
        self.print_line(prompt_value, value)
        return False

    def evaluate_value(self, prompt_value, value):
        """
        Checks the current value against the regular expression
        :param prompt_value:
        :param value:
        :return:
        """
        self.match = self.re_eval.fullmatch(value)
        if self.match is not None:
            return True
        else:
            return self.evaluate_failed(prompt_value, value)

    def handle_cancel(self):
        """
        Can be used for extra processing when the user aborts the input
        :return:
        """
        return

    def handle_delete(self, prompt_value, value):
        """
        Removes characters from the end of the current value
        :param prompt_value:
        :param value:
        :return:
        """
        self.clear_line(prompt_value, value)
        if len(value) > 0:
            value = value[:-1]
        self.print_line(prompt_value, value)
        return value

    def handle_insert(self, prompt_value, value, char):
        """
        Appends characters to the end of the current value
        :param prompt_value:
        :param value:
        :param char:
        :return:
        """
        if 32 <= ord(char) <= 125:  # only printable characters
            value += char
        self.clear_line(prompt_value, value)
        self.print_line(prompt_value, value)
        return value

    def convert_value(self, value):
        """
        Converts text to some other type, used in subclasses
        :param value:
        :return:
        """
        return value

    def __call__(self, prompt_val, *args, **kwargs):
        """
        Echoes the prompt and then processing input one character at a time
        until the user pushes enter to start validation and conversion
        :param prompt_val:
        :param args:
        :param kwargs:
        :return:
        """
        # echo the prompt before reading input
        print(prompt_val, end='', flush=True)
        ret_val = ""

        # break on enter, bail on ctrl+c/d
        while True:
            c = getch()

            if ord(c) == 13:  # carriage return
                #  User has pressed enter, evaluate_value
                if self.evaluate_value(prompt_val, ret_val):
                    break

            elif ord(c) in [3, 4, 27]:  # ctrl+c, ctrl+d, escape
                #  Exit if ctrl+c/d or escape are pressed
                self.handle_cancel()
                ret_val = None
                break

            elif ord(c) in [8, 127]:  # backspace, delete
                ret_val = self.handle_delete(prompt_val, ret_val)

            else:  # all other character
                ret_val = self.handle_insert(prompt_val, ret_val, c)

        print('\n', end='', flush=True)
        if ret_val is not None:
            ret_val = self.convert_value(ret_val)

        return ret_val
