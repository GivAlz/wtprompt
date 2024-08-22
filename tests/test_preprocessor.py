from wtPrompt.utils.preprocessor import TextPreprocessor

def test_default_preprocessor():
    preprocessor = TextPreprocessor()
    assert preprocessor.preprocess(" this is a test.    Hello"), (True, 'this is a test.  Hello')
    assert preprocessor.preprocess("I wonder how\n\n\nthis works"), (True, 'I wonder how  this works')
    assert preprocessor.preprocess(' '), (False, '')

def test_preprocessor_json():
    preprocessor = TextPreprocessor.load_from_json('test_prompts/preprocessor_config.json')
    assert preprocessor.preprocess("a"), (False, 'a')
    assert preprocessor.preprocess("abcdefghilmn"), (True, "abcdefghil")
    assert preprocessor.preprocess("ab1237816237816312"), (False, "ab12378162")

def test_preprocessor_inline():
    preprocessor = TextPreprocessor(do_truncate=True, max_length=10)
    assert preprocessor.preprocess("abcdefghilmn hola"), (True, "abcdefghil")
