import os
import json


class ValidationError(Exception):
    """Custom exception class for validation errors."""
    pass


def validate_json(filepath: str) -> bool:
    """
    Validates a JSON file to ensure it exists, is a valid JSON,
    and that its content is a dictionary where values are either
    dictionaries (with the same type of validation) or strings.

    :param filepath: The path to the JSON file to validate.
    :return: True if the file is valid; otherwise, raises a ValidationError.
    """

    def validate_dict(d: dict) -> bool:
        """
        Recursively validate that a dictionary's values are either
        dictionaries or strings.

        :param d: The dictionary to validate.
        :return: True if the dictionary is valid; otherwise, raises a ValidationError.
        """
        if not isinstance(d, dict):
            raise ValidationError("The content must be a dictionary.")

        for key, value in d.items():
            if isinstance(value, dict):
                # Recursively validate nested dictionaries
                validate_dict(value)
            elif isinstance(value, str):
                continue  # Valid string value
            else:
                raise ValidationError(
                    f"Value associated with key '{key}' is not a valid type. Must be a dictionary or string.")

        return True

    # Check if the file exists
    if not os.path.isfile(filepath):
        raise ValidationError(f"The provided path '{filepath}' is not a valid file.")

    # Load and validate JSON content
    with open(filepath, 'r', encoding='utf-8') as file:
        try:
            content = json.load(file)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Error decoding JSON file {filepath}: {e}")

    # Validate the content
    validate_dict(content)

    # If all checks pass, return True
    return True
