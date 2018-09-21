import queue
import re
import threading
import time


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

    def start_input(self):
        self.impl.start_input()

    def stop_input(self):
        self.impl.stop_input()


class _GetchUnix(object):
    def __init__(self, *args, **kwargs):
        super(_GetchUnix, self).__init__(*args, **kwargs)
        import tty, sys, termios, select, os
        self._sys = sys
        self._termios = termios
        self._tty = tty
        self._select = select
        self._fd = None
        self._old_settings = None
        self._os = os

    def __call__(self):
        if self._select.select([self._sys.stdin], [], [], 0)[0]:
            # ch = self._sys.stdin.read(1)
            ch = self._os.read(self._fd, 50).decode('utf-8')
        else:
            ch = None

        return ch

    def start_input(self):
        self._fd = self._sys.stdin.fileno()
        self._old_settings = self._termios.tcgetattr(self._fd)
        self._tty.setraw(self._fd)
        self._tty.setcbreak(self._fd, self._termios.TCSANOW)

    def stop_input(self):
        self._termios.tcsetattr(
            self._fd,
            self._termios.TCSADRAIN,
            self._old_settings
        )


class _GetchWindows(object):
    def __init__(self, *args, **kwargs):
        super(_GetchWindows, self).__init__(*args, **kwargs)
        import msvcrt
        self._msvcrt = msvcrt
        self.char_queue = queue.Queue(16)
        self.thread = threading.Thread(target=self.stdin_loop)
        self.thread.run()

    def stdin_loop(self, *args, **kwargs):
        while True:
            c = self._msvcrt.getch()
            self.char_queue.put(c)

    def __call__(self):
        try:
            return self.char_queue.get_nowait()
        except queue.Empty as e:
            return None

    def start_input(self):
        return

    def stop_input(self):
        return


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
        self.cursor_pos = None

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

    def move_cursor_left(self, n):
        print(u"\u001b[{}D".format(n), end='', flush=True)

    def print_line(self, prompt_value, value, end=''):
        """
        Echoes the current line in its entirety
        :param prompt_value:
        :param value:
        :param end:
        :return:
        """
        print("{}{}".format(prompt_value, value), end=end, flush=True)
        if self.cursor_pos < len(value):
            self.move_cursor_left((len(value) - self.cursor_pos))

    def evaluate_failed(self, prompt_value, value):
        """
        Provides feedback when input does not validate against the regular
        expression
        :param prompt_value:
        :param value:
        :return:
        """
        getch.stop_input()
        print("\nInvalid input, try again.")
        self.print_line(prompt_value, value)
        getch.start_input()
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
        if len(value) > 0 and (self.cursor_pos - 1) >= 0:
            self.cursor_pos -= 1
            value = value[:self.cursor_pos] + value[self.cursor_pos+1:]
        self.print_line(prompt_value, value)
        return value

    def cursor_left(self, prompt_value, value):
        if (self.cursor_pos - 1) >= 0:
            self.cursor_pos -= 1
            return True
        return False

    def cursor_right(self, prompt_value, value):
        if (self.cursor_pos + 1) < len(value) + 1:
            self.cursor_pos += 1
            return True
        return False

    def handle_escape_sequence(self, prompt_value, value, sequence):
        """

        :param prompt_value:
        :param value:
        :param sequence:
        :return:
        """
        allow_echo = False

        c, d, _arrow = list(sequence)
        if _arrow == 'A':  # up
            pass
        elif _arrow == 'B':  # down
            pass
        elif _arrow == 'C':  # right
            allow_echo = self.cursor_right(prompt_value, value)
        elif _arrow == 'D':  # left
            allow_echo = self.cursor_left(prompt_value, value)
        else:  # some other escape sequence
            pass
        return allow_echo

    def handle_insert(self, prompt_value, value, char):
        """
        Appends characters to the end of the current value
        :param prompt_value:
        :param value:
        :param char:
        :return:
        """
        if 32 <= ord(char) <= 125:  # only printable characters
            value = value[:self.cursor_pos] + char + value[self.cursor_pos:]
            self.cursor_pos += 1
            self.clear_line(prompt_value, value)
            self.print_line(prompt_value, value)
            # print("value: {}\tpos: {}".format(value, self.cursor_pos))
            return value
        else:
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
        # self.cursor_pos = len(prompt_val)
        self.cursor_pos = 0
        ret_val = ""

        getch.start_input()
        # break on enter, bail on ctrl+c/d
        while True:
            c, d, e = getch(), None, None
            esc_seq = None
            if c is None:
                continue

            if len(c) == 3:
                esc_seq = c
                c, d, e = list(c)

            if ord(c) == 13:  # carriage return
                #  User has pressed enter, evaluate_value
                if self.evaluate_value(prompt_val, ret_val):
                    break

            elif ord(c) in [3, 4, 27]:  # ctrl+c, ctrl+d, escape
                #  Exit if ctrl+c/d or escape are pressed
                if ord(c) != 27 or d is None:
                    self.handle_cancel()
                    ret_val = None
                    break

                if self.handle_escape_sequence(prompt_val, ret_val, esc_seq):
                    print(esc_seq, end='', flush=True)

            elif ord(c) in [8, 127]:  # backspace, delete
                ret_val = self.handle_delete(prompt_val, ret_val)

            else:  # all other character
                ret_val = self.handle_insert(prompt_val, ret_val, c)

        getch.stop_input()

        print('\n', end='', flush=True)
        if ret_val is not None:
            ret_val = self.convert_value(ret_val)

        return ret_val
