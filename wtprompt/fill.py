import re
import warnings

from jinja2 import Template
from jinja2.sandbox import SandboxedEnvironment

from typing import Dict, List

class PromptGenerator:
    """Base class used to fill the variables inside a prompt.

    The prompt should be formatter using Jinja2 template syntax

    """
    def __init__(self):
        """Initialises the necessary classes by Jinja.

        """
        self._sandbox_env = SandboxedEnvironment()
        self._compiled_templates = {}
        self._necessary_variables = {}

    def get_or_compile_prompt(self, prompt_text: str) -> Template:
        """Get a prompt Template, compiling it if necessary.

        :param prompt_text: Text for the prompt
        :return: Compiled Jinja2 Template object
        """
        if compiled_prompt := self._compiled_templates.get(prompt_text):
            return compiled_prompt
        compiled_prompt = self._sandbox_env.from_string(prompt_text)
        self._compiled_templates[prompt_text] = compiled_prompt
        return compiled_prompt

    def fill_prompt(self, prompt_text, variables: Dict[str, str]) -> str:
        """Fill a prompt.

        The prompt should be formatted using Jinja syntax. This syntax is very expressive and powerful but,
        in its most basic form, you can write the prompt as follows:

            This is a prompt {{key_1}}.

        Passing the prompt_name together with a dictionary {'key_1': 'value'}, this method will
        substitute key_1 with the value.

        If {{key_1}} appears multiple times, it will substitute it multiple times.

        REMARK: the name for the keys can contain only the chars matched by the regex: [a-zA-z0-9_]

        :param prompt_text: The text of the prompt
        :param fillers: Dictionary with arguments to be used to fill the prompt
        :return: prompt text with the substituted key/values.
        """
        prompt_template = self.get_or_compile_prompt(prompt_text)
        result = prompt_template.render(variables)
        return result

_PLACEHOLDER = r'[{]{2}([a-zA-Z0-9_ ]*)[}]{2}'

def fill_list(prompt_text: str, values: List[str]) -> str:
    """Basic function to fill a prompt.

    Given a prompt with a list of placeholders in the form {{}} or {{name}} replaces them in order using values from
    the values list.

    Remark: the substitution function ignores variable names and substitutes matches in order.

    It expects to find the same number of placeholders and values.
    """
    placeholders = re.findall(_PLACEHOLDER, prompt_text)

    if len(values) != len(placeholders):
        warnings.showwarning(f"Using {len(values)} values to fill {len(placeholders)} placeholders:"
                             "These should have the same length!\nPlease check your prompt or input!", Warning)

    def replacement(match):
        if _ := match.group(1):
            value = values.pop(0)
            return value
        return match.group(0)

    prompt_text = re.sub(_PLACEHOLDER, replacement, prompt_text)

    return prompt_text
