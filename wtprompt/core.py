from __future__ import annotations

import json
import os
import warnings

from abc import abstractmethod
from typing import Dict, Optional, Union

from pydantic import BaseModel, Field, field_validator


class PromptLoader(BaseModel):
    """Abstract class to manage prompt loading.

    This class is meant as a "datastructure": it manages and stores prompts.
    """
    prompts: Dict[str, Union[str, PromptLoader]] = Field(default_factory=dict,
                                                         description="Dictionary to store prompt contents.")

    def __init__(self, **data):
        # Loading using pydantic validators
        super().__init__(**data)
        self.load()

    @abstractmethod
    def load(self):
        pass

    def get_prompt_list(self):
        return self.prompts

    def add_prompt(self, prompt_name: str, prompt_text: str):
        if prompt_name in self.prompts:
            warnings.showwarning(f"Prompt {prompt_name} already present.\n"
                                 f"Please check the prompt names!\nAdding nothing.", Warning)
            return
        self.prompts[prompt_name] = prompt_text

    def _get_prompt(self, name: str) -> str:
        # Recursive function to get a prompt based on a potentially nested name.

        if '/' in name:
            current_key, other_keys = name.split('/', 1)
            return self.prompts[current_key]._get_prompt(other_keys)

        if name in self.prompts:
            return self.prompts[name]

        raise ValueError(f"No such prompt: '{name}'")

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


class FolderPrompts(PromptLoader):
    """Load prompts from a folder.

    Usage:

        prompts = FolderPrompts(prompt_folder="/path/to/folder")

    where the folder contains .txt and .md files
    """
    prompt_folder: str = Field('', description="The folder containing .txt and .md files.")

    @field_validator('prompt_folder')
    def validate_folder(cls, dirname):
        if not os.path.isdir(dirname) and not dirname == '':
            raise ValueError(f"The provided path '{dirname}' is not a valid directory.")
        return dirname

    def load(self):
        """Loads .txt and .md files from the folder into the prompts dictionary."""
        if self.prompt_folder == '':
            return
        self._load_from_folder(self.prompt_folder, self.prompts)

    @staticmethod
    def _load_from_folder(folder_path, prompts_dict):
        """Recursively loads files from the given folder path into the provided prompts dictionary."""
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                prompts_dict[item] = FolderPrompts(prompt_folder=item_path)
            elif item.endswith('.txt') or item.endswith('.md'):
                with open(item_path, 'r', encoding='utf-8') as file:
                    prompt_name = os.path.splitext(item)[0]
                    prompts_dict[prompt_name] = file.read()


class JsonPrompts(PromptLoader):
    """Load prompts from a json file.

    Usage:

        prompts = JsonPrompts(prompt_file="/path/to/prompts.json")

    The json should contain a dictionary of the kind: {'prompt name': 'prompt text'}
    """
    prompt_file: str = Field('', description="The .json file containing the prompts.")

    @field_validator('prompt_file')
    def validate_json(cls, prompt_file):
        if prompt_file == '':
            return
        # Validating if the file exists, it is a valid json, the content is a dictionary
        if not os.path.isfile(prompt_file):
            raise ValueError(f"The provided path '{prompt_file}' is not a valid file.")

        # Load and validate JSON content
        with open(prompt_file, 'r', encoding='utf-8') as file:
            try:
                content = json.load(file)
            except json.JSONDecodeError as e:
                raise ValueError(f"Error decoding JSON file {prompt_file}: {e}")

        # Validate that the content is a dictionary with string keys and values
        if not isinstance(content, dict):
            raise ValueError("The content of the file is not a dictionary.")
        for key, value in content.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise ValueError(f"All keys and values in the dictionary must be strings."
                                 f"Found key: {key}, value: {value}")
        return prompt_file

    def load(self):
        if self.prompt_file == '':
            return
        """Loads the json into the prompts dictionary."""
        with open(self.prompt_file, 'r', encoding='utf-8') as file:
            self.prompts = json.load(file)
