from __future__ import annotations

import json
import os
import warnings

from typing import Optional, Union, Any

from pydantic import BaseModel, Field, field_validator


class PromptLoader(BaseModel):
    """Base class to manage prompt loading.
    """
    def __init__(self, **data):
        # Loading using pydantic validators
        super().__init__(**data)
        self._prompts = {}

    def add_prompt(self, prompt_name: str, prompt_text: str):
        if prompt_name in self._prompts:
            warnings.showwarning(f"Prompt {prompt_name} already present.\n"
                                 f"Please check the prompt names!\nAdding nothing.", Warning)
            return
        self._prompts[prompt_name] = prompt_text

    def _get_prompt_text(self, prompt_name: str):
        return self._prompts[prompt_name]

    def get_prompts(self):
        return self._prompts

    def __getattr__(self, prompt_name: str) -> str:
        """Access prompt content via attribute-style access.

        Example:
            To access the content of a prompt named 'hello', use:

                prompt_class_instance.hello

        :param name (str): The name of the prompt to access.

        :returns: The content of the prompt if it exists, otherwise throws an attribute error.
        """
        return self._get_prompt_text(prompt_name)

    def __call__(self, prompt_name: str) -> Optional[str]:
        """Access prompt content via function-call-style access.

        Example:
            To access the content of a prompt named 'hello', use:

                prompt_class_instance('hello')

        :param prompt_name (str): The name of the prompt to access.

        :returns: The content of the prompt if it exists, otherwise throws an attribute error.
        """
        return self._get_prompt_text(prompt_name)


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

    def _get_prompt_text(self, prompt_name: str):
        if prompt_name in self._prompts:
            return self._prompts[prompt_name]
        # Prompt not found: loading it
        prompt_text = self._load_prompt_from_file(prompt_name)
        self._prompts[prompt_name] = prompt_text
        return prompt_text

    def _load_prompt_from_file(self, prompt_name: str) -> str:
        prompt_name = os.path.join(self.prompt_folder, prompt_name)
        file_extensions = ['.md', '.txt']

        for ext in file_extensions:
            file_path = f"{prompt_name}{ext}"
            if os.path.isfile(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read().strip()

        raise FileNotFoundError(f"No .txt or .md file found for '{prompt_name}'. Can't load the prompt!")

    def load(self):
        """Loads .txt and .md files from the folder into the prompts dictionary."""
        if self.prompt_folder == '':
            return
        self._load_from_folder(self.prompt_folder)

    def _load_from_folder(self, folder_path):
        """Recursively loads files from the given folder path into the provided prompts dictionary."""
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                self._load_from_folder(folder_path=item_path)
            elif item.endswith('.txt') or item.endswith('.md'):
                with open(item_path, 'r', encoding='utf-8') as file:
                    prompt_name = os.path.relpath(item_path, self.prompt_folder)
                    self._prompts[prompt_name] = file.read()

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

    def load(self):
        if self.prompt_file == '':
            return
        """Loads the json into the prompts dictionary."""
        with open(self.prompt_file, 'r', encoding='utf-8') as file:
            self._prompts = json.load(file)
