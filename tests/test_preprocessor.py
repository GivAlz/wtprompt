import unittest

from jinja2.filters import do_truncate

from wtPrompt.utils.preprocessor import TextPreprocessor


class TestBase(unittest.TestCase):

    def test_default_preprocessor(self):
        preprocessor = TextPreprocessor()
        self.assertEqual(preprocessor.preprocess(" this is a test.    Hello"), (True, 'this is a test.  Hello'))
        self.assertEqual(preprocessor.preprocess("I wonder how\n\n\nthis works"), (True, 'I wonder how  this works'))
        self.assertEqual(preprocessor.preprocess(' '), (False, ''))

    def test_preprocessor_json(self):
        preprocessor = TextPreprocessor.load_from_json('test_prompts/preprocessor_config.json')
        self.assertEqual(preprocessor.preprocess("a"), (False, 'a'))
        self.assertEqual(preprocessor.preprocess("abcdefghilmn"), (True, "abcdefghil"))
        self.assertEqual(preprocessor.preprocess("ab1237816237816312"), (False, "ab12378162"))

    def test_preprocessor_inline(self):
        preprocessor = TextPreprocessor(do_truncate=True, max_length=10)
        self.assertEqual(preprocessor.preprocess("abcdefghilmn hola"), (True, "abcdefghil"))
        