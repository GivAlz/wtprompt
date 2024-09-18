from __future__ import annotations

import hashlib
import json
import os
import pathlib
import warnings

from typing import Optional, Union, Tuple

from pydantic import BaseModel, Field, field_validator

from wtprompt.utils.json_validator import validate_json


class PromptLoader(BaseModel):
    """Base class to manage prompt loading.
    """
    def __init__(self, **data):
        # Loading using pydantic validators
        super().__init__(**data)
        self._prompts = {}
        self._prompt_hashes = {}

    def add_prompt(self, prompt_name: str, prompt_text: str):
        """Add a single prompt, with prompt_name and prompt_text.

        This function stores the prompt and its hash inside the calss.
        """
        if prompt_name in self._prompts:
            warnings.showwarning(f"Prompt {prompt_name} already present.\n"
                                 f"Please check the prompt names!\nAdding nothing.", Warning)
            return
        self._prompts[prompt_name] = prompt_text
        # Computing and storing hash
        computed_hash = hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()
        self._prompt_hashes[prompt_name] = computed_hash

    def _get_prompt_text(self, prompt_name: str):
        return self._prompts[prompt_name]

    def get_prompt_with_hash(self, prompt_name: str) -> Tuple[str, str]:
        """Get a single prompt and its hash.

        :param prompt_name: name of the prompt to be retrieved
        """
        return self._prompts[prompt_name], self._prompt_hashes[prompt_name]

    def get_prompt(self, prompt_name: str) -> str:
        """Get a single prompt and, optionally, its hash.

        :param prompt_name: name of the prompt to be retrieved
        """
        return self._prompts[prompt_name]

    def save_prompt_report(self, outfile: str):
        """Saving hashes to outfile.

        This is useful for prompt versioning.
        """
        outfile = pathlib.Path(outfile).with_suffix('.json')
        with open(outfile, 'w') as f:
            json.dump(self._prompt_hashes, f)

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

    def __str__(self):
        if self._pre_prompt:
            raise ValueError(f"ERROR: self._pre_prompt must be empty but has value {self._pre_prompt}\n"
                             f"This is likely caused by using the '.' operator to extract a prompt which silently"
                             f"failed.")
        return super().__str__()

    @field_validator('prompt_folder')
    def validate_folder(cls, dirname):
        if not os.path.isdir(dirname) and not dirname == '':
            raise ValueError(f"The provided path '{dirname}' is not a valid directory.")
        return dirname

    def load_from_prompt_report(self, prompt_report: str, strict: bool=True):
        """Loads the prompt listed in the prompt_report.

        :param prompt_report: file containing the prompt_report
        :param strict: (Optional) if set to True (default) it will throw an error whenever the has is different
            from the saved one.

        """
        prompt_report =  pathlib.Path(prompt_report).with_suffix('.json')
        with open(prompt_report, 'r') as f:
            prompt_hashes = json.load(f)

        for prompt_name, prompt_hash in prompt_hashes.items():
            _ = self._get_prompt_text(prompt_name)
            if strict:
                computed_hash = self._prompt_hashes[prompt_name]
                if computed_hash != prompt_hash:
                    message = ("Prompt {prompt_name} has different hash!\n"
                               "Expected hash: {prompt_hash}\nLoaded hash: {computed_hash}")
                    raise ValueError(message)


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
        self.add_prompt(prompt_name=prompt_name,
                        prompt_text=prompt_text)
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
                    self.add_prompt(prompt_name=prompt_name,
                                    prompt_text=file.read())

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
            prompts = json.load(file)
            for prompt_name, prompt_text in prompts.items():
                self.add_prompt(prompt_name=prompt_name,
                                prompt_text=prompt_text)
