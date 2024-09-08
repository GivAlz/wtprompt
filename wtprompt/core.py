from __future__ import annotations

import hashlib
import json
import os
import pathlib
import warnings

from typing import Optional, Union

from pydantic import BaseModel, Field, field_validator

from wtprompt.utils.json_validator import validate_json


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

    def save_prompt_report(self, outfile: str):
        # Hashing prompts
        prompt_hashes = {}
        for key, prompt in self._prompts.items():
            prompt_hashes[key] = hashlib.sha256(prompt.encode("utf-8")).hexdigest()

        # Saving report
        outfile = pathlib.Path(outfile).with_suffix('.json')
        with open(outfile, 'w') as f:
            json.dump(prompt_hashes, f)

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

    def __init__(self, **data):
        # Loading using pydantic validators
        super().__init__(**data)
        self._pre_prompt = ''

    @field_validator('prompt_folder')
    def validate_folder(cls, dirname):
        if not os.path.isdir(dirname) and not dirname == '':
            raise ValueError(f"The provided path '{dirname}' is not a valid directory.")
        return dirname

    def load_from_prompt_report(self, outfile: str):
        outfile =  pathlib.Path(outfile).with_suffix('.json')
        with open(outfile, 'r') as f:
            prompt_hashes = json.load(f)

        for prompt_name, prompt_hash in prompt_hashes.items():
            prompt_text = self._get_prompt_text(prompt_name)
            computed_hash = hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()
            if computed_hash != prompt_hash:
                warnings.showwarning(f"Prompt {prompt_name} has different has!\n"
                                     f"Expected hash: {prompt_hash}\nLoaded hash: {computed_hash}", Warning)


    def _temp_prompt_folder(self, prompt_folder: str):
        if prompt_folder:
            self._pre_prompt = os.path.join(self._pre_prompt, prompt_folder)
        else:
            self._pre_prompt = ''

    def __getattr__(self, prompt_name: str) -> Union[str, FolderPrompts]:
        """Access prompt content via attribute-style access.

        Example:
            To access the content of a prompt named 'hello', use:

                prompt_class_instance.hello

        :param name (str): The name of the prompt to access.

        :returns: The content of the prompt if it exists, otherwise throws an attribute error.
        """
        prompt_name = os.path.join(self._pre_prompt, prompt_name)
        # Trying to load the prompt from memory or from file
        prompt_text = self._prompts.get(prompt_name)
        if prompt_text is None:
            prompt_text = self._load_prompt_from_file(prompt_name)

        if isinstance(prompt_text, str):
            self._temp_prompt_folder('')
            return prompt_text
        # Last possibility: this is a folder
        self._temp_prompt_folder(prompt_name)
        # TODO: This approach is buggy as, if a text is not found, it will end up returning a FolderPrompts object
        return self

    def _get_prompt_text(self, prompt_name: str):
        if prompt_name in self._prompts:
            return self._prompts[prompt_name]
        # Prompt not found: loading it
        prompt_text = self._load_prompt_from_file(prompt_name)
        if prompt_name is None:
            raise FileNotFoundError(f"No .txt or .md file found for '{prompt_name}'. Can't load the prompt!")
        self._prompts[prompt_name] = prompt_text
        return prompt_text

    def _load_prompt_from_file(self, prompt_name: str) -> str:
        prompt_name = os.path.join(self.prompt_folder, prompt_name)
        file_extensions = ['.md', '.txt']

        for ext in file_extensions:
            file_path = pathlib.Path(prompt_name).with_suffix(ext)
            if os.path.isfile(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read().strip()

        return None

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
    validate_json: bool = Field(False, description="If True evaluates the JSON before loading it.")

    def __init__(self, **data):
        super().__init__(**data)
        if self.validate_json:
            validate_json(self.prompt_file)
        # No support for lazy loading for json
        self.load()

    def load(self):
        if self.prompt_file == '':
            return
        """Loads the json into the prompts dictionary."""
        with open(self.prompt_file, 'r', encoding='utf-8') as file:
            self._prompts = json.load(file)
