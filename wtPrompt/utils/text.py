import json

from typing import Tuple
from pydantic import BaseModel, field_validator, model_validator

from wtPrompt.utils.basic_operations import do_strip, check_empty, spaces_only, max_consecutive_spaces, text_truncate, \
    ascii_only, text_normalize, check_letters, has_min_length


class TextPreprocessorValidator(BaseModel):
    do_strip: bool = True
    check_empty: bool = True
    check_letters: bool = False
    percentage_letters: float = 0.85
    truncate: bool = False
    max_length: int = -1
    min_length: int = -1
    spaces_only: bool = True
    max_consecutive_spaces: int = 2
    ascii_only: bool = False
    unicode_normalize: str = ''

    @field_validator('unicode_normalize')
    def validate_unicode_normalize(cls, v):
        if v not in ['', 'NFC', 'NFKC', 'NFD', 'NFKD']:
            raise ValueError(
                f"Invalid normalize form: '{v}'. Valid options are: ['NFC', 'NFKC', 'NFD', 'NFKD']")
        return v

    @field_validator('max_length')
    def max_length_valid(cls, v):
        if v < -1 or v == 0:
            raise ValueError('max_length must be -1 or a positive integer')
        return v

    @field_validator('min_length')
    def min_length_valid(cls, v):
        if v < -1:
            raise ValueError('min_length must be -1 or a positive integer')
        return v

    @field_validator('max_consecutive_spaces')
    def max_consecutive_spaces_positive(cls, v):
        if v <= 0:
            raise ValueError('max_consecutive_spaces must be a positive integer')
        return v

    @field_validator('percentage_letters')
    def percentage_chars_valid(cls, v):
        if v < 0 or v >= 1:
            raise ValueError('percentage_chars must be between 0 and 1')
        return v

    @model_validator(mode='after')
    def check_max_min_length(cls, values):
        max_length = values.get('max_length')
        min_length = values.get('min_length')
        if max_length < min_length and not (max_length == -1 or min_length == -1):
            raise ValueError('max_length must be greater than or equal to min_length')
        return values

class TextPreprocessor:
    """
    TextPreprocessor
    ---------------

    Basic text preprocessing and validation class.

    Parameters:
        do_strip (bool): If True calls the function .strip() on the string
        check_empty (bool): If True, the preprocessor will return False and an empty string if
            the input text is empty (after stripping whitespace).
        check_letters (bool): If True, the preprocessor will check if the percentage of letters in the text is at
            least `percentage_letters`. If not, it will return False and the original text.
        percentage_letters (float): The minimum percentage of letters required in the text if `check_letters` is True. Must be between 0 and 1.
        truncate (bool): If True, the preprocessor will truncate the text to the `max_length` if it exceeds that length.
        max_length (int): The maximum length of the text after preprocessing. If set to -1, there is no maximum length.
        min_length (int): The minimum length of the text after preprocessing. If set to -1, there is no minimum length.
        spaces_only (bool): If True, the preprocessor will replace all whitespace characters with a single space.
        max_consecutive_spaces (int): The maximum number of consecutive spaces allowed in the text.
            If set to 1, the preprocessor will replace all consecutive spaces with a single space.
        ascii_only (bool): If True, the preprocessor will keep only ASCII characters in the text.
        unicode_normalize (str): The Unicode normalization form to apply to the text, e.g., 'NFC' or 'NFD'.
            See the `unicodedata.normalize()` documentation for valid options.

    Raises:
        ValueError: If any of the input parameters are invalid.

    Returns:
        Tuple[bool, str]: A tuple where the first element is a boolean indicating whether the preprocessing
        was successful, and the second element is the preprocessed text.
    """
    def __init__(self, **kwargs):
        self.settings = TextPreprocessorValidator(**kwargs)
        self.preprocessing_pipeline = self.setup_pipeline()
        if not self.preprocessing_pipeline:
            raise ValueError("Preprocessing pipeline is empty. Please configure at least one preprocessing step.")

    @staticmethod
    def load_from_json(json_file: str) -> 'TextPreprocessor':
        with open(json_file, 'r') as f:
            params = json.load(f)

        return TextPreprocessor(**params)

    def setup_pipeline(self):
        preprocessing_pipeline = []
        if self.settings.do_strip:
            preprocessing_pipeline.append(do_strip)

        if self.settings.check_empty:
            preprocessing_pipeline.append(check_empty)

        if self.settings.spaces_only:
            preprocessing_pipeline.append(spaces_only)

        if self.settings.max_consecutive_spaces > 0:
            preprocessing_pipeline.append(
                lambda text: max_consecutive_spaces(text, self.settings.max_consecutive_spaces))

        if self.settings.truncate and -1 < self.settings.max_length:
            preprocessing_pipeline.append(lambda text: text_truncate(text, self.settings.max_length))

        if self.settings.ascii_only:
            preprocessing_pipeline.append(ascii_only)

        if self.settings.unicode_normalize:
            preprocessing_pipeline.append(lambda text: text_normalize(text, self.settings.unicode_normalize))

        if self.settings.check_letters:
            preprocessing_pipeline.append(lambda text: check_letters(text, self.settings.percentage_letters))

        if self.settings.min_length > -1:
            preprocessing_pipeline.append(lambda text: has_min_length(text, self.settings.min_length))

        return preprocessing_pipeline

    def get_preprocessing_pipeline(self):
        """Getting the pipeline which can then be modified.
        """
        return self.preprocessing_pipeline

    def update_preprocessing_pipeline(self):
        """Saving directly the preprocessing pipeline.

        Do this at your own risk.
        """
        return self.preprocessing_pipeline

    def preprocess(self, text: str) -> Tuple[bool, str]:
        is_ok = True
        for prep_f in self.preprocessing_pipeline:
            is_ok, text = prep_f(text)
            if not is_ok:
                break
        return is_ok, text

