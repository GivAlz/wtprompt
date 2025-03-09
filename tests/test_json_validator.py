import os
import pytest

from wtprompt.utils.json_validator import is_json_valid, ValidationError


def test_correct_json(test_folder_location):
    assert is_json_valid(os.path.join(test_folder_location, 'test_prompts', 'test.json'))

    with pytest.raises(ValidationError):
        is_json_valid(os.path.join(test_folder_location, 'preprocessor_config.json'))

