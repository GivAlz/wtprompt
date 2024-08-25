from __future__ import annotations

import json
from typing import Tuple, List
from pydantic import Field, BaseModel, field_validator, model_validator

from wtprompt.utils.basic_operations import (
    do_strip,
    check_empty,
    spaces_only,
    max_consecutive_spaces,
    text_truncate,
    ascii_only,
    text_normalize,
    check_letters,
    has_min_length,
)


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
        do_truncate (bool): If True, the preprocessor will truncate the text to the `max_length`
            if it exceeds that length.
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
    do_strip: bool = True
    check_empty: bool = True
    check_letters: bool = False
    percentage_letters: float = Field(0.85, gt=0, le=1, description="Float, a percentage in [0,1]")
    do_truncate: bool = False
    max_length: int = -1
    min_length: int = Field(0, gt=-1, description="For no min_len -1, otherwise a positive integer")
    spaces_only: bool = True
    max_consecutive_spaces: int = Field(2, gt=-1,
                                        description="Integer, -1 for no limit on consecutive integer, positive "
                                                    "for a limit on them.")
    ascii_only: bool = False
    unicode_normalize: str = ''
    preprocessing_pipeline: List = []

    def __init__(self, /, **kwargs):
        super().__init__(**kwargs)
        self.preprocessing_pipeline = self.build_pipeline()
        if not self.preprocessing_pipeline:
            raise ValueError("Preprocessing pipeline is empty. Please configure at least one preprocessing step.")

    def build_pipeline(self):
        preprocessing_pipeline = []
        if self.do_strip:
            preprocessing_pipeline.append(do_strip)

        if self.check_empty:
            preprocessing_pipeline.append(check_empty)

        if self.spaces_only:
            preprocessing_pipeline.append(spaces_only)

        if self.max_consecutive_spaces > 0:
            preprocessing_pipeline.append(
                lambda text: max_consecutive_spaces(text, self.max_consecutive_spaces))

        if self.do_truncate and -1 < self.max_length:
            preprocessing_pipeline.append(lambda text: text_truncate(text, self.max_length))

        if self.ascii_only:
            preprocessing_pipeline.append(ascii_only)

        if self.unicode_normalize:
            preprocessing_pipeline.append(lambda text: text_normalize(text, self.unicode_normalize))

        if self.check_letters:
            preprocessing_pipeline.append(lambda text: check_letters(text, self.percentage_letters))

        if self.min_length > -1:
            preprocessing_pipeline.append(lambda text: has_min_length(text, self.min_length))

        return preprocessing_pipeline

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

    @model_validator(mode='after')
    def check_max_min_length(cls, values):
        max_length = values.max_length
        min_length = values.min_length
        if max_length < min_length and not (max_length == -1 or min_length == -1):
            raise ValueError('max_length must be greater than or equal to min_length')
        return values

    @classmethod
    def load_from_json(cls, json_file: str) -> TextPreprocessor:
        with open(json_file, 'r') as f:
            params = json.load(f)

        return cls(**params)

    def get_preprocessing_pipeline(self):
        """Getting the pipeline.

        This allows you to modify the pipeline externally and then save the modified version using
        update_preprocessing_pipeline.

        Make sure that the functions you add have the following signature

        def function_name(text: str) -> Tuple[bool, str]:
        """
        return self.preprocessing_pipeline

    def update_preprocessing_pipeline(self, modified_pipeline):
        """Saving directly the preprocessing pipeline.

        See above the correct function signature; beware of potential errors.
        """
        self.preprocessing_pipeline = modified_pipeline


    def preprocess(self, text: str) -> Tuple[bool, str]:
        is_ok = True
        for prep_f in self.preprocessing_pipeline:
            is_ok, text = prep_f(text)
            if not is_ok:
                break
        return is_ok, text
