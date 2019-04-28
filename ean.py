# -*- coding: utf-8 -*-
"""\
Utilities to check if a code is a valid EAN-13/EAN-8/UPC-A code.

References:
- The `International Article Number<<https://en.wikipedia.org/wiki/International_Article_Number>`>`_ page on Wikipedia.
- The `ean<https://github.com/arthurdejong/python-stdnum/blob/master/stdnum/ean.py>`_ module in the ``stdnum`` library.
"""


def compute_check_digit(number: str) -> str:
    """\
    Computes the check-digit of a given EAN-13/EAN-8/UPC-A code.
    
    Args:
        number: The code *without* its last digit.
        
    Returns:
        As described above.
    """
    # Digits at odd-numbered (resp. even-numbered) positions have a weight of 3 (resp. 1):
    weighted_sum = sum((3, 1)[i % 2] * int(digit) for i, digit in enumerate(reversed(number)))
    check_digit = (10 - weighted_sum % 10)
    return str(check_digit)


def validate(code: str) -> str:
    """\
    Checks whether the given code is a valid EAN-13/EAN-8/UPC-A code in terms of length and check-digit.
    
    Raises:
        ValueError: If the check fails.
        
    Returns:
        A compact version of the code.
    """
    code = code.strip()
    if not code.isdigit():
        raise ValueError("invalid format")
    if len(code) not in (13, 12, 8):
        raise ValueError("invalid length")
    if compute_check_digit(code[:-1]) != code[-1]:
        raise ValueError("invalid check-digit")
    return code


def is_valid(code: str) -> bool:
    """\
    Check whether the given code is a valid EAN-13/EAN-8/UPC-A code in terms of length and check-digit.
    """
    try:
        validate(code)
        return True
    except ValueError:
        return False
