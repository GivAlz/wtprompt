import unittest

from wtPrompt.core import FolderPrompts, JsonPrompts


class TestBasePrompts(unittest.TestCase):

    def test_folder_prompts(self):
        base_prompts = FolderPrompts(prompt_folder='test_prompts')
        assert(base_prompts.hello == base_prompts('hello') == 'Say hello!')
        assert(base_prompts.test == base_prompts('test') == 'This is a test prompt.')

    def test_json_prompts(self):
        base_prompts = JsonPrompts(prompt_file='test_prompts/test.json')
        assert(base_prompts.test == base_prompts('test') == 'this is a test')

    def test_prompts_fill(self):
        base_prompts = FolderPrompts(prompt_folder='test_prompts')
        target_str = "This is a test: today is Monday August."
        self.assertEqual(target_str,
                         base_prompts.fill("fill_test", {'day':'Monday','this_month': 'August'}))

        self.assertEqual(target_str, base_prompts.fill_list("list_fill_test", ['Monday', 'August']))
