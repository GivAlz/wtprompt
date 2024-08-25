import os.path

import pytest
from pydantic import ValidationError

from wtprompt.core import FolderPrompts, JsonPrompts, PromptLoader
from wtprompt.fill import PromptGenerator, fill_list

def test_prompt_loader():
    prompt_loader = PromptLoader()
    prompt_loader.add_prompt('test', 'content')
    assert prompt_loader('test') == 'content'

def test_folder_prompts(test_folder_location):
    base_prompts = FolderPrompts(prompt_folder=os.path.join(test_folder_location, 'test_prompts'))
    # lazy load -> the second time it uses the cached version
    for i in range(2):
        assert base_prompts('hello') == 'Say hello!'
        assert base_prompts('test') == 'This is a test prompt.'
        # assert base_prompts.subfolder.nested == 'This is a nested prompt.' # Currently not working
        assert base_prompts('subfolder/nested') == 'This is a nested prompt.'

def test_json_prompts(test_folder_location):
    base_prompts = JsonPrompts(prompt_file=os.path.join(test_folder_location, 'test_prompts', 'test.json'))
    assert base_prompts('test') == 'this is a test'

def test_prompts_fill(test_folder_location):
    base_prompts = FolderPrompts(prompt_folder=os.path.join(test_folder_location, 'test_prompts'))
    target_str = "This is a test: today is Monday August."

    p_gen = PromptGenerator()
    assert p_gen.fill_prompt(base_prompts.fill_test, {'day': 'Monday', 'this_month': 'August'}) == target_str
    assert p_gen.fill_prompt(base_prompts.fill_test, {'this_month': 'August', 'day': 'Monday'}) == target_str
    assert fill_list(base_prompts.fill_test, ['Monday', 'August']) == target_str

    target_str = "This is a test: today is August Monday."
    assert fill_list(base_prompts.fill_test, ['August', 'Monday']) == target_str

    a = 'fill'
    modified_prompt_1 = p_gen.fill_prompt('Test {{ a }} and {{a}}', {'a': a})
    modified_prompt_2 = p_gen.fill_prompt('Test {{ a }} and {{a}}', {'a': a})
    assert modified_prompt_1 == modified_prompt_2 == 'Test fill and fill'


def test_loading_errors():
    prompt_file = 'non_existent.json'
    # Use pytest's raises context manager to catch the AssertionError
    with pytest.raises(ValidationError, match=f"The provided path '{prompt_file}' is not a valid file."):
        base_prompts = JsonPrompts(prompt_file=prompt_file)

    prompt_folder = 'non_existent'
    with pytest.raises(ValidationError, match=f"The provided path '{prompt_folder}' is not a valid directory."):
        base_prompts = FolderPrompts(prompt_folder=prompt_folder)

    print("AssertionError correctly raised for non-existent file/directory.")

    base_prompts = FolderPrompts()
    base_prompts = JsonPrompts()
    print("Created empty prompt classes!")
