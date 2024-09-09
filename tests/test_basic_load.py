import os.path

import tempfile
import pytest

from wtprompt import FolderPrompts, JsonPrompts, PromptLoader
from wtprompt import PromptGenerator, fill_list

def test_prompt_loader():
    prompt_loader = PromptLoader()
    prompt_loader.add_prompt('test', 'content')
    assert prompt_loader('test') == 'content'

def test_folder_prompts(test_folder_location):
    test_folder = os.path.join(test_folder_location, 'test_prompts')
    base_prompts = FolderPrompts(prompt_folder=test_folder)
    # lazy load -> the second time it uses the cached version
    for i in range(2):
        assert base_prompts('hello') == 'Say hello!'
        assert base_prompts.hello == 'Say hello!'
        assert base_prompts('test') == 'This is a test prompt.'
        assert base_prompts.test == base_prompts('test')

        # assert base_prompts.subfolder.nested == 'This is a nested prompt.' # Currently not working
        assert base_prompts('subfolder/nested') == 'This is a nested prompt.'
        assert base_prompts.subfolder.nested == base_prompts('subfolder/nested')

    with tempfile.NamedTemporaryFile() as temp_file:
        base_prompts.save_prompt_report(temp_file.name)

        new_base_prompts = FolderPrompts(prompt_folder=test_folder)
        new_base_prompts.load_from_prompt_report(temp_file.name)
        loaded_keys = new_base_prompts._prompts.keys()
        assert 'hello' in loaded_keys and 'test' in loaded_keys
        assert 'subfolder/nested'in loaded_keys

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
    with pytest.raises(FileNotFoundError):
        base_prompts = JsonPrompts(prompt_file=prompt_file)

    prompt_folder = 'non_existent'
    with pytest.raises(ValueError):
        base_prompts = FolderPrompts(prompt_folder=prompt_folder)

    print("AssertionError correctly raised for non-existent file/directory.")

    base_prompts = FolderPrompts()
    base_prompts = JsonPrompts()
    print("Created empty prompt classes!")
