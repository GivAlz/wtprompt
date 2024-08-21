import os
import warnings

from typing import Dict, Optional
from pydantic import BaseModel, Field, ValidationError, field_validator


class BasePrompts(BaseModel):
    """Base class to load prompts.

    Usage:

        prompts = Prompts(folder="/path/to/folder")



    """
    prompt_folder: str = Field(..., description="The folder containing .txt and .md files.")
    prompts: Dict[str, str] = Field(default_factory=dict, description="Dictionary to store file contents.")

    def __init__(self, **data):
        # Loading using pydantic validators
        super().__init__(**data)
        self.load()

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

    def _get(self, name: str) -> str:
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
        return self._get(name)

    def __call__(self, name: str) -> Optional[str]:
        """Access prompt content via function-call-style access.

        Example:
            To access the content of a prompt named 'hello', use:

                prompt_class_instance('hello')

        :param name (str): The name of the prompt to access.

        :returns: The content of the prompt if it exists, otherwise throws an attribute error.
        """
        return self._get(name)