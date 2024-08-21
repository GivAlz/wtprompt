import unittest

from wtPrompt.core import BasePrompts

class TestBase(unittest.TestCase):

    def test_forward_rnn(self):
        base_prompts = BasePrompts(prompt_folder='test_prompts')
        assert(base_prompts.hello == base_prompts('hello') == 'Say hello!')
        assert(base_prompts.test == base_prompts('test') == 'This is a test prompt.')