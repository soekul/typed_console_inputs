from .base import RegExInputValidatorMethod


import datetime
import decimal
import re


INT_RE = re.compile(r"^[0-9]{1,3}(,?[0-9]{3})*$")
DECIMAL_RE = re.compile(r"^[0-9]{1,3}(,?[0-9]{3})*(\.[0-9]+)?$")
MONEY_RE = re.compile(r"^\$?[0-9]{1,3}(,?[0-9]{3})*(\.[0-9]+)?$")


YEAR_RE_STR = r"(?P<{}year>\d{{4}})"
MONTH_RE_STR = r"(?P<{}month>(0?[1-9])|(1[012]))"
DAY_RE_STR = r"(?P<{}day>(0?[1-9])|([12][0-9])|(3[01]))"
DATE_DELIMITER_RE_STR = r"[-/]"
GROUPED_DD_RE_STR = r"(?P<{{}}delimiter>{})".format(DATE_DELIMITER_RE_STR)


def standard_date_dict(label):
    return {
        'year': YEAR_RE_STR.format(label),
        'month': MONTH_RE_STR.format(label),
        'day': DAY_RE_STR.format(label),
        'delimiter': DATE_DELIMITER_RE_STR,
        'grouped_delimiter': GROUPED_DD_RE_STR.format(label),
    }


DATE_RE = re.compile(
    r"^({yyyymmdd})|({mmddyyyy})$".format(
        yyyymmdd=r"{year}{grouped_delimiter}{month}{delimiter}{day}".format(
            **standard_date_dict('A')
        ),
        mmddyyyy=r"{month}{grouped_delimiter}{day}{delimiter}{year}".format(
            **standard_date_dict('B')
        )
    )
)
# DATE_RE = re.compile(r"^((?P<Ayear>\d{4})[-/](?P<Amonth>(0?[1-9])|(1[012]))[-/](?P<Aday>(0?[1-9])|([12][0-9])|(3[01])))|((?P<Bmonth>(0?[1-9])|(1[012]))[-/](?P<Bday>(0?[1-9])|([12][0-9])|(3[01]))[-/](?P<Byear>\d{4}))$")


class CommaDelimitedNumericBase(RegExInputValidatorMethod):
    def convert_value(self, value):
        return value.replace(",", '')  # remove commas before casting


class IntInputMethod(CommaDelimitedNumericBase):
    re_eval = INT_RE

    def convert_value(self, value):
        return int(super(IntInputMethod, self).convert_value(value))


class FloatInputMethod(CommaDelimitedNumericBase):
    re_eval = DECIMAL_RE

    def convert_value(self, value):
        return float(super(FloatInputMethod, self).convert_value(value))


class DecimalInputMethod(CommaDelimitedNumericBase):
    re_eval = DECIMAL_RE

    def convert_value(self, value):
        return decimal.Decimal(
            super(DecimalInputMethod, self).convert_value(value)
        )


class DateInputMethod(RegExInputValidatorMethod):
    re_eval = DATE_RE

    def __init__(self, *args, **kwargs):
        super(DateInputMethod, self).__init__(*args, **kwargs)
        self._dt_obj = None

    def _parse_date(self, value):
        delimiter = self.match.group('Adelimiter') \
                    or self.match.group('Bdelimiter')
        fmt_str = "%Y{delim}%m{delim}%d".format(delim=delimiter)
        if self.match.group('Ayear') is None:
            fmt_str = "%m{delim}%d{delim}%Y".format(delim=delimiter)
        return datetime.datetime.strptime(value, fmt_str)

    def evaluate_value(self, prompt_value, value):
        match_valid = super(DateInputMethod, self)\
            .evaluate_value(prompt_value, value)

        if match_valid is False:
            return match_valid
        try:
            self._dt_obj = self._parse_date(value)
        except ValueError as e:
            return self.evaluate_failed(prompt_value, value)
        else:
            return match_valid

    def convert_value(self, value):
        return self._dt_obj


class MaskedInputMethod(RegExInputValidatorMethod):
    mask_char = '*'

    def __init__(self, mask_char=None, *args, **kwargs):
        super(MaskedInputMethod, self).__init__(*args, **kwargs)
        if mask_char is not None:
            self.mask_char = mask_char

    def print_line(self, prompt_value, value, end=''):
        input_mask = ""
        if self.mask_char != '':
            input_mask = self.mask_char * len(value)
        print("{}{}".format(prompt_value, input_mask), end=end, flush=True)
        if self.cursor_pos < len(value):
            self.move_cursor_left((len(value) - self.cursor_pos))

    def __call__(self, prompt_val, mask_char=None, *args, **kwargs):
        old_char = None
        if mask_char is not None and mask_char != self.mask_char:
            old_char = self.mask_char
            self.mask_char = mask_char
        ret_val = super(MaskedInputMethod, self)\
            .__call__(prompt_val, *args, **kwargs)
        if old_char is not None:
            self.mask_char = old_char
        return ret_val


int_input = IntInputMethod()
float_input = FloatInputMethod()
money_input = FloatInputMethod(MONEY_RE)
decimal_input = DecimalInputMethod()
date_input = DateInputMethod()
password_input = MaskedInputMethod()
