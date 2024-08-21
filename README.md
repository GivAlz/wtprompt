# 🤌 wtPrompt (What the Prompt?)

A lightweight, no-nonsense library for managing your LLM prompts.

Tired of cluttering your code with blocks of text? wtPrompt lets you keep your code clean by loading prompts from text files. Say goodbye to length issues and linting headaches.

## How to Use

Gather all your prompts into a folder, e.g. `folder_path`, saving them as `.txt` or `.md` files.

Then, simply run the following code:
    
    from wtPrompt.core import BasePrompts

    my_prompts = BasePrompts(prompt_folder='folder_path')

    # Now the following will return your prompt in .str format
    my_prompts.prompt_name
    my_prompts('prompt_name')

Where the prompt name is given by the file name, e.g., `hello.txt` can be loaded as `hello`.
