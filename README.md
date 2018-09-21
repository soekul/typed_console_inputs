# Typed Console Inputs
Provides methods that validate, sanitize and type cast input from console

## Install
`pip install git+https://github.com/soekul/typed_console_inputs.git`

## Example Usage
```
>>> import typed_console_inputs as tci
>>> int_val = tci.int_input("IeatINTS: ")
IeatINTS: 1,000,000,0.00
Invalid input, try again.
IeatINTS: 1,000,000.00
Invalid input, try again.
IeatINTS: 1,000,000
>>> print("Type: {}\tValue: {}".format(type(int_val), int_val))
Type: <class 'int'>     Value: 1000000
>>> float_val = tci.float_input("Feed me floats: ")
Feed me floats: 100,000.14159.3
Invalid input, try again.
Feed me floats: 100000.14159
>>> print("Type: {}\tValue: {}".format(type(float_val), float_val))
Type: <class 'float'>   Value: 100000.14159
>>> decimal_val = tci.decimal_input("Enter decimal: ")
Enter decimal: 123,456.9876543210001
>>> print("Type: {}\tValue: {}".format(type(decimal_val), decimal_val))
Type: <class 'decimal.Decimal'> Value: 123456.9876543210001
>>> money_val = tci.fmoney_input("I like money a lot: ")
I like money a lot: $1234321654.3542
>>> print("Type: {}\tValue: {}".format(type(money_val), money_val))
Type: <class 'float'>   Value: 1234321654.3542
>>> hex_val = tci.hex_input("Enter hex: ")
Enter hex: 1A4
Invalid input, try again.
Enter hex: 0x1a4.00
Invalid input, try again.
Enter hex: 0xdeadbeef
>>> print("Type: {}\tValue: {}".format(type(hex_val), hex_val))
Type: <class 'int'>     Value: 3735928559
>>> date_val = tci.date_input("Care for a date? ")
Care for a date? 13/10/2004
Invalid input, try again.
Care for a date? 2003-02-29
Invalid input, try again.
Care for a date? 2003-02-28
>>> print("Type: {}\tValue: {}".format(type(date_val), date_val))
Type: <class 'datetime.datetime'>       Value: 2003-02-28 00:00:00
>>> pass_val = tci.password_input("Setec Astronomy? ")
Setec Astronomy? ****************************
>>> print("Type: {}\tValue: {}".format(type(pass_val), pass_val))
Type: <class 'str'>     Value: Correct-Horse-Battery-Staple
>>>
```
