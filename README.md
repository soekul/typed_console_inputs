# Typed Console Inputs
Provides methods that validate, sanitize and type cast input from console

## Example Usage

### Standard Integer
```
>>> import typed_console_inputs as tci
>>> int_val = tci.int_input("Please provide an integer input: ")
Please provide an integer input:  1.0
Invalid input, try again.
Please provide an integer input:  asdf
Invalid input, try again.
Please provide an integer input:  1,0
Invalid input, try again.
Please provide an integer input:  1,000
>>> print("type: {}\t value: {}".format(type(int_val), int_val))
type: <class 'int'>	 value: 1000 
```


### Passwords
```
>>> from typed_console_inputs  import password_input
>>> _tv = password_input("Please enter your password: ")
Please enter your password:  ****************************
>>> print(_tv)
Correct-Horse-Battery-Staple
>>> _tv = password_input("Please enter your password: ", mask_char='')
Please enter your password:
>>> print(_tv)
Some-Other-Password
```
