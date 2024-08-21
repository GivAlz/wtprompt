import re
import unicodedata
from typing import Tuple
from pydantic import BaseModel, field_validator, model_validator


class TextPreprocessor(BaseModel):
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
        normalize (str): The Unicode normalization form to apply to the text, e.g., 'NFC' or 'NFD'.
            See the `unicodedata.normalize()` documentation for valid options.

    Raises:
        ValueError: If any of the input parameters are invalid.

    Returns:
        Tuple[bool, str]: A tuple where the first element is a boolean indicating whether the preprocessing
        was successful, and the second element is the preprocessed text.
    """
    do_strip: bool = True
    check_empty: bool = False
    check_letters: bool = False
    percentage_letters: float = 0.8
    truncate: bool = False
    max_length: int = -1
    min_length: int = -1
    spaces_only: bool = True
    max_consecutive_spaces: int = 1
    ascii_only: bool = False
    normalize: str = ''

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
    def check_max_min_length(cls, self):
        if self.max_length < self.min_length and not (self.max_length == -1 or self.min_length == -1):
            raise ValueError('max_length must be greater than or equal to min_length')

    def preprocess(self, text: str) -> Tuple[bool, str]:

        if self.do_strip:
            text = text.strip()

        if self.check_empty and not text:
            return False, text

        if self.spaces_only:
            text = re.sub(r'\s', ' ', text)

        if self.max_consecutive_spaces > 1:
            text = re.sub(rf'\s{{{self.max_consecutive_spaces+1},}}', ' ' * self.max_consecutive_spaces, text)

        if self.truncate and -1 < self.max_length < len(text):
            text = text[:self.max_length]

        if self.ascii_only:
            text = text.encode('ascii', 'ignore').decode('ascii')

        if self.normalize:
            text = unicodedata.normalize(self.normalize, text)

        if self.check_letters:
            letters = sum(c.isalpha() for c in text)
            total_chars = len(text)
            if total_chars == 0 or letters / total_chars < self.percentage_chars:
                return False, text

        if self.min_length > -1 and len(text) < self.min_length:
            return False, text

        return True, text
