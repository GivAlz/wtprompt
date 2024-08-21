import unittest

from wtPrompt.utils.basic_operations import do_strip, check_empty, spaces_only, max_consecutive_spaces, text_truncate, \
    ascii_only, text_normalize, check_letters, has_min_length


class TestTextPreprocessing(unittest.TestCase):
    def test_do_strip(self):
        self.assertEqual(do_strip("   hello world   "), (True, "hello world"))
        self.assertEqual(do_strip(""), (True, ""))

    def test_check_empty(self):
        self.assertEqual(check_empty(""), (False, ""))
        self.assertEqual(check_empty("hello"), (True, "hello"))

    def test_spaces_only(self):
        self.assertEqual(spaces_only("hello world\n"), (True, "hello world "))
        self.assertEqual(spaces_only("hello world\t "), (True, "hello world  "))

    def test_max_consecutive_spaces(self):
        self.assertEqual(max_consecutive_spaces("   hello   world   ", 1), (True, " hello world "))
        self.assertEqual(max_consecutive_spaces("   hello   world   ", 2),
                         (True, "  hello  world  "))

    def test_text_truncate(self):
        self.assertEqual(text_truncate("hello world", 5), (True, "hello"))
        self.assertEqual(text_truncate("hello world", 100), (True, "hello world"))

    def test_ascii_only(self):
        self.assertEqual(ascii_only("hello world"), (True, "hello world"))
        self.assertEqual(ascii_only("hélló wórld"), (True, "hll wrld"))

    def test_text_normalize(self):
        self.assertEqual(text_normalize("hélló wórld", "NFC"), (True, "hélló wórld"))

    def test_check_letters(self):
        self.assertEqual(check_letters("hello world", 0.5), (True, "hello world"))
        self.assertEqual(check_letters("12345 world", 0.5), (False, "12345 world"))

    def test_has_min_length(self):
        self.assertEqual(has_min_length("hello world", 5), (True, "hello world"))
        self.assertEqual(has_min_length("hello", 10), (False, "hello"))

if __name__ == '__main__':
    unittest.main()