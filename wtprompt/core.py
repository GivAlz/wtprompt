from __future__ import annotations

import json
import os

from typing import Dict, Optional, Union, Any

from pydantic import BaseModel, Field, field_validator


class PromptLoader(BaseModel):
    """Base class to manage prompt loading.

    This class can only
    """
    def __init__(self, **data):
        # Loading using pydantic validators
        super().__init__(**data)
        self._prompts = {} #Dictionary to store prompt sub structure

    def _get_prompt_text(self, prompt_name: str, full_path: str):
        try:
            return self.prompts[prompt_name]
        except ValueError:
            raise ValueError(f"Prompt {full_path} not found!")

    def get_prompts(self):
        return self._prompts

    def _get_prompt(self, prompt_name: str, full_path: str) -> str:
        if '/' in prompt_name:
            current_key, other_keys = prompt_name.split('/', 1)
            if not (sub_folder := self._prompts.get(current_key)):
                self._prompts[current_key] = sub_folder = PromptLoader()
            sub_folder.get_or_add_prompt(other_keys, full_path)

        if prompt_name in self._prompts:
            return self._prompts[prompt_name]

        self._prompts[prompt_name] = prompt_text = self._get_prompt_text(prompt_name, full_path)
        return prompt_text

    def __getattr__(self, name: str) -> str:
        """Access prompt content via attribute-style access.

        Example:
            To access the content of a prompt named 'hello', use:

                prompt_class_instance.hello

        :param name (str): The name of the prompt to access.

        :returns: The content of the prompt if it exists, otherwise throws an attribute error.
        """
        return self._get_prompt(name, name)

    def __call__(self, name: str) -> Optional[str]:
        """Access prompt content via function-call-style access.

        Example:
            To access the content of a prompt named 'hello', use:

                prompt_class_instance('hello')

        :param name (str): The name of the prompt to access.

        :returns: The content of the prompt if it exists, otherwise throws an attribute error.
        """
        return self._get_prompt(name, name)


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

    def _get_prompt_text(self, prompt_name: str, full_path: str):
        full_path = os.path.join(self.prompt_folder, full_path)
        md_path = f"{full_path}.md"
        if os.path.isfile(md_path):
            with open(md_path, 'r', encoding='utf-8') as file:
                return file.read().strip()

        txt_path = f"{full_path}.txt"
        if os.path.isfile(txt_path):
            with open(txt_path, 'r', encoding='utf-8') as file:
                return file.read().strip()

        # If neither .txt nor .md file is found, raise an error
        raise FileNotFoundError(
            f"No .txt or .md file found for '{prompt_name}' at '{full_path}'. Can't load the prompt!")

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

    def __init__(self, **data):
        super().__init__(**data)
        # No support for lazy loading for json
        self.load()

    def load(self, prompt_dictionary: Dict[str, Any] = None):
        if prompt_dictionary is None:
            if self.prompt_file == '':
                return
            """Loads the json into the prompts dictionary."""
            with open(self.prompt_file, 'r', encoding='utf-8') as file:
                prompt_dictionary = json.load(file)
        self._load_from_json(prompt_dictionary)


    @staticmethod
    def _load_from_json(prompts_dict):
        """Recursively loads files from the given folder path into the provided prompts dictionary."""
        for p_name, p_value in prompts_dict.items():
            if isinstance(p_value, dict):
                prompts_dict[p_name] = JsonPrompts(prompt_dictionary=p_value)
            elif isinstance(p_value, str):
                prompts_dict[p_name] = p_value
            else:
                raise ValueError(f"JSON incorrectly formatted, can't find {p_value} is not a valid prompt!")
