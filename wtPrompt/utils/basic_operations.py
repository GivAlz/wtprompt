"""Text Preprocessing Utilities

This module provides a set of utility functions for performing basic text preprocessing operations and checks.
These functions are designed to be used with the text preprocessing pipeline implemented in the
`TextPreprocessor` class.

The general scheme for these functions is:

    input -> the text to be processed
    output -> a tuple of (bool, str)
        - The boolean value indicates whether the preprocessing was successful or not.
        - The string value is the processed text.

If a function requires additional parameters beyond the input text, they should be added as keyword arguments
to the function. This allows the function to be integrated into the preprocessing pipeline doing:

    lambda text: my_function(text, variable=value)

Functions:
    do_strip(text: str) -> Tuple[bool, str]:
        Strips leading and trailing whitespace from the input text.

    check_empty(text: str) -> Tuple[bool, str]:
        Checks if the input text is empty (after stripping whitespace) and returns False if it is.

    spaces_only(text: str) -> Tuple[bool, str]:
        Replaces all whitespace characters with a single space.

    max_consecutive_spaces(text: str, max_spaces: int) -> Tuple[bool, str]:
        Reduces consecutive spaces to the specified maximum number of spaces.

    truncate(text: str, max_length: int) -> Tuple[bool, str]:
        Truncates the input text to the specified maximum length, if it exceeds that length.

    ascii_only(text: str) -> Tuple[bool, str]:
        Keeps only ASCII characters in the input text.

    normalize(text: str, normalize_form: str) -> Tuple[bool, str]:
        Applies the specified Unicode normalization form to the input text.

    check_letters(text: str, percentage_letters: float) -> Tuple[bool, str]:
        Checks if the percentage of letters in the input text is at least the specified minimum,
        and returns False if it is not.

    min_length(text: str, min_length: int) -> Tuple[bool, str]:
        Checks if the length of the input text is at least the specified minimum, and returns False if it is not.
"""
import re
import unicodedata
from typing import Tuple


def do_strip(text: str) -> Tuple[bool, str]:
    return True, text.strip()

def check_empty(text: str) -> Tuple[bool, str]:
    return (False, text) if not text else (True, text)

def spaces_only(text: str) -> Tuple[bool, str]:
    text = re.sub(r'\s', ' ', text)
    return True, text

def max_consecutive_spaces(text: str, max_spaces) -> Tuple[bool, str]:
    text = re.sub(rf'\s{{{max_spaces + 1},}}', ' ' * max_spaces, text)
    return True, text

def text_truncate(text: str, max_length) -> Tuple[bool, str]:
    if 0 < max_length:
        text = text[:max_length]
    return True, text

def ascii_only(text: str) -> Tuple[bool, str]:
    return True, text.encode('ascii', 'ignore').decode('ascii')

def text_normalize(text: str, normalize_form) -> Tuple[bool, str]:
    return True, unicodedata.normalize(normalize_form, text)

def check_letters(text: str, percentage_letters) -> Tuple[bool, str]:
    letters = sum(c.isalpha() for c in text)
    total_chars = len(text)
    if total_chars == 0 or letters / total_chars < percentage_letters:
        return False, text
    return True, text

def has_min_length(text: str, min_len) -> Tuple[bool, str]:
    if len(text) < min_len:
        return False, text
    return True, text
