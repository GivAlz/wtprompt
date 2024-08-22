import os.path

from wtPrompt.core import FolderPrompts, JsonPrompts


def test_folder_prompts(test_folder_location):
    base_prompts = FolderPrompts(prompt_folder=os.path.join(test_folder_location, 'test_prompts'))
    assert base_prompts('hello') == 'Say hello!'
    assert base_prompts('test') == 'This is a test prompt.'

def test_json_prompts(test_folder_location):
    base_prompts = JsonPrompts(prompt_file=os.path.join(test_folder_location, 'test_prompts', 'test.json'))
    assert base_prompts('test') == 'this is a test'

def test_prompts_fill(test_folder_location):
    base_prompts = FolderPrompts(prompt_folder=os.path.join(test_folder_location, 'test_prompts'))
    target_str = "This is a test: today is Monday August."
    assert base_prompts.fill("fill_test", {'day': 'Monday', 'this_month': 'August'}) == target_str
    assert base_prompts.fill_list("list_fill_test", ['Monday', 'August']) == target_str
