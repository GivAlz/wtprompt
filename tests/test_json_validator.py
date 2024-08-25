import os
import pytest

from wtprompt.utils.json_validator import validate_json, ValidationError


def test_correct_json(test_folder_location):
    assert validate_json(os.path.join(test_folder_location, 'test_prompts', 'test.json'))

    with pytest.raises(ValidationError):
        validate_json(os.path.join(test_folder_location, 'preprocessor_config.json'))

