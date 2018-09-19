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
    def __call__(self, *args, **kwargs):
        ret_val = super(CommaDelimitedNumericBase, self)\
            .__call__(*args, **kwargs)
        return ret_val.replace(",", '')  # remove commas before casting


class IntInputMethod(CommaDelimitedNumericBase):
    re_eval = INT_RE

    def __call__(self, *args, **kwargs):
        ret_val = super(IntInputMethod, self).__call__(*args, **kwargs)
        return int(ret_val)


class FloatInputMethod(CommaDelimitedNumericBase):
    re_eval = DECIMAL_RE

    def __call__(self, *args, **kwargs):
        ret_val = super(FloatInputMethod, self).__call__(*args, **kwargs)
        return float(ret_val)


class DecimalInputMethod(CommaDelimitedNumericBase):
    re_eval = DECIMAL_RE

    def __call__(self, *args, **kwargs):
        ret_val = super(DecimalInputMethod, self).__call__(*args, **kwargs)
        return decimal.Decimal(ret_val)


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

    def __call__(self, *args, **kwargs):
        ret_val = super(DateInputMethod, self).__call__(*args, **kwargs)
        return self._dt_obj


int_input = IntInputMethod()
float_input = FloatInputMethod()
money_input = FloatInputMethod(MONEY_RE)
decimal_input = DecimalInputMethod()
date_input = DateInputMethod()
