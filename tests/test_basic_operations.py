from wtprompt.utils.basic_operations import (
    do_strip,
    check_empty,
    spaces_only,
    max_consecutive_spaces,
    text_truncate,
    ascii_only,
    text_normalize,
    check_letters,
    has_min_length)

def test_do_strip():
    assert do_strip("   hello world   "), (True, "hello world")
    assert do_strip(""), (True, "")

def test_check_empty():
    assert check_empty(""), (False, "")
    assert check_empty("hello"), (True, "hello")

def test_spaces_only():
    assert spaces_only("hello world\n"), (True, "hello world ")
    assert spaces_only("hello world\t "), (True, "hello world  ")

def test_max_consecutive_spaces():
    assert max_consecutive_spaces("   hello   world   ", 1), (True, " hello world ")
    assert max_consecutive_spaces("   hello   world   ", 2), (True, "  hello  world  ")

def test_text_truncate():
    assert text_truncate("hello world", 5), (True, "hello")
    assert text_truncate("hello world", 100), (True, "hello world")

def test_ascii_only():
    assert ascii_only("hello world"), (True, "hello world")
    assert ascii_only("hélló wórld"), (True, "hll wrld")

def test_text_normalize():
    assert text_normalize("hélló wórld", "NFC"), (True, "hélló wórld")

def test_check_letters():
    assert check_letters("hello world", 0.5), (True, "hello world")
    assert check_letters("12345 world", 0.5), (False, "12345 world")

def test_has_min_length():
    assert has_min_length("hello world", 5), (True, "hello world")
    assert has_min_length("hello", 10), (False, "hello")
