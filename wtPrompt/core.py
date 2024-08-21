import json
import os
import re
import warnings
from abc import abstractmethod

from typing import Dict, Optional, List
from pydantic import BaseModel, Field, ValidationError, field_validator


class BasePrompts(BaseModel):
    """Abstract class to manage prompts.

    """
    prompts: Dict[str, str] = Field(default_factory=dict, description="Dictionary to store file contents.")

    def __init__(self, **data):
        # Loading using pydantic validators
        super().__init__(**data)
        self.load()

    @abstractmethod
    def load(self):
        pass

    def get_prompt_list(self):
        return self.prompts

    def add_prompt(self, prompt_name:str, prompt_text: str):
        self.prompts[prompt_name] = prompt_text

    def _get_prompt(self, name: str) -> str:
        """Gets a prompt; internal function.
        """
        if name in self.prompts:
            return self.prompts[name]
        raise AttributeError(f"No such prompt: '{name}'")

    def __getattr__(self, name: str) -> str:
        """Access prompt content via attribute-style access.

        Example:
            To access the content of a prompt named 'hello', use:

                prompt_class_instance.hello

        :param name (str): The name of the prompt to access.

        :returns: The content of the prompt if it exists, otherwise throws an attribute error.
        """
        return self._get_prompt(name)

    def __call__(self, name: str) -> Optional[str]:
        """Access prompt content via function-call-style access.

        Example:
            To access the content of a prompt named 'hello', use:

                prompt_class_instance('hello')

        :param name (str): The name of the prompt to access.

        :returns: The content of the prompt if it exists, otherwise throws an attribute error.
        """
        return self._get_prompt(name)

    def fill(self, prompt_name: str, fillers) -> str:
        """Fill a prompt.

        The prompt should be formatted in the following way:

            This is a prompt {{key_1}}.

        Passing the prompt_name together with a dictionary {'key_1': 'value'}, this method will
        substitute key_1 with the value.

        If {{key_1}} appears multiple times, it will substitute it multiple times.

        REMARK: the name for the keys can contain only the chars matched by the regex: [a-zA-z0-9_]

        :param prompt_name: Name of the prompt
        :param fillers: Dictionary with arguments to be used to fill the prompt
        :return: prompt text with the substituted key/values.
        """
        filled_prompt = self.prompts[prompt_name]
        # Find all the placeholders in the prompt text
        placeholders = re.findall(r'\{\{(.[a-zA-Z0-9_]+?)?}\}', filled_prompt)

        # Substitute the placeholders
        for placeholder in placeholders:
            if placeholder in fillers:
                filled_prompt = filled_prompt.replace('{{%s}}' % placeholder, str(fillers[placeholder]))
            else:
                warnings.showwarning(f"Warning: {placeholder} not found in prompt!\n"
                                     f"It can't be substituted: please check your prompt or input!", Warning)
        return filled_prompt


    def fill_list(self, prompt_name: str, values: List[str]) -> str:
        """Fill a prompt.

        Similar to the fill method, the main difference is that it substitutes the place orders, which can be the same
        ones used in the fill method or even {{}} in order.

        It expects to find the same number of placeholders and values.
        """
        filled_prompt = self.prompts[prompt_name]
        placeholders = re.findall(r'\{\{(.[a-zA-Z0-9_]*?)?}\}', filled_prompt)

        if len(values) != len(placeholders):
            warnings.showwarning(f"Using {len(values)} values to fill {len(placeholders)} placeholders:"
                                 "These should have the same length!\nPlease check your prompt or input!", Warning)
        for i, placeholder in enumerate(placeholders):
            if i < len(values):
                filled_prompt = filled_prompt.replace('{{%s}}' % placeholder, str(values[i]))
            else:
                break

        return filled_prompt

class FolderPrompts(BasePrompts):
    """Load prompts from a folder.

    Usage:

        prompts = FolderPrompts(prompt_folder="/path/to/folder")

    where the folder contains .txt and .md files
    """
    prompt_folder: str = Field(..., description="The folder containing .txt and .md files.")

    @field_validator('prompt_folder')
    def validate_folder(cls, dirname):
        if not os.path.isdir(dirname):
            raise ValidationError(f"The provided path '{dirname}' is not a valid directory.")
        return dirname

    def load(self):
        """Loads .txt and .md files from the folder into the prompts dictionary."""
        for file_name in os.listdir(self.prompt_folder):
            if file_name.endswith('.txt') or file_name.endswith('.md'):
                file_path = os.path.join(self.prompt_folder, file_name)
                with open(file_path, 'r', encoding='utf-8') as file:
                    prompt_name = os.path.splitext(file_name)[0]
                    if prompt_name in self.prompts:
                        warnings.showwarning(f"Prompt {prompt_name} already present.\n"
                                             f"You likely have two files with the name {prompt_name} and "
                                             f"different extensions.\nPlease either remove one of the files "
                                             f"or change one file's name", Warning)
                        continue
                    self.prompts[prompt_name] = file.read()

class JsonPrompts(BasePrompts):
    """Load prompts from a json file.

    Usage:

        prompts = JsonPrompts(prompt_file="/path/to/prompts.json")

    The json should contain a dictionary of the kind: {'prompt name': 'prompt text'}
    """
    prompt_file: str = Field(..., description="The .json file containing the prompts.")

    @field_validator('prompt_file')
    def validate_json(cls, prompt_file):
        # Validating if the file exists, it is a valid json, the content is a dictionary
        if not os.path.isfile(prompt_file):
            raise ValidationError(f"The provided path '{prompt_file}' is not a valid file.")

        # Load and validate JSON content
        with open(prompt_file, 'r', encoding='utf-8') as file:
            try:
                content = json.load(file)
            except json.JSONDecodeError as e:
                raise ValidationError(f"Error decoding JSON file {prompt_file}: {e}")

        # Validate that the content is a dictionary with string keys and values
        if not isinstance(content, dict):
            raise ValidationError(f"The content of the file is not a dictionary.")
        for key, value in content.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise ValidationError(f"All keys and values in the dictionary must be strings."
                                      f"Found key: {key}, value: {value}")
        return prompt_file

    def load(self):
        """Loads the json into the prompts dictionary."""
        with open(self.prompt_file, 'r', encoding='utf-8') as file:
            self.prompts = json.load(file)
