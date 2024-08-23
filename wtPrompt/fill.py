import re
import warnings

from typing import Dict, List


def fill_prompt(prompt_text: str, fillers: Dict[str, str]) -> str:
    """Fill a prompt.

    The prompt should be formatted in the following way:

        This is a prompt {{key_1}}.

    Passing the prompt_name together with a dictionary {'key_1': 'value'}, this method will
    substitute key_1 with the value.

    If {{key_1}} appears multiple times, it will substitute it multiple times.

    REMARK: the name for the keys can contain only the chars matched by the regex: [a-zA-z0-9_]

    :param prompt_text: The text of the prompt
    :param fillers: Dictionary with arguments to be used to fill the prompt
    :return: prompt text with the substituted key/values.
    """
    # Substitute the placeholders
    def replace_placeholder(match):
        if (placeholder := match.group("placeholder")) in fillers:
            return str(fillers[placeholder])
        return match.group(0)  # Returns the original text, including `{{` and `}}`

    prompt_text = re.sub(r'[{]{2}(?P<placeholder>[a-zA-Z0-9_]+?)[}]{2}', replace_placeholder, prompt_text)
    return prompt_text


def fill_list(prompt_text: str, values: List[str]) -> str:
    """Fill a prompt.

    Similar to the fill method, the main difference is that it substitutes the place orders, which can be the same
    ones used in the fill method or even {{}} in order.

    It expects to find the same number of placeholders and values.
    """
    placeholders = re.findall(r'[{]{2}([a-zA-Z0-9_]*)[}]{2}', prompt_text)

    if len(values) != len(placeholders):
        warnings.showwarning(f"Using {len(values)} values to fill {len(placeholders)} placeholders:"
                             "These should have the same length!\nPlease check your prompt or input!", Warning)

    def replacement(match):
        if _ := match.group(1):
            value = values.pop(0)
            return value
        return match.group(0)

    prompt_text = re.sub(r'\{\{([a-zA-Z0-9_]*?)?}\}', replacement, prompt_text)

    return prompt_text
