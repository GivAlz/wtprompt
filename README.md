# 🤌 wtPrompt (What the Prompt?)

A lightweight, no-nonsense library for managing your LLM prompts.

Tired of cluttering your code with blocks of text? wtPrompt lets you keep your code clean by loading prompts from text files. Say goodbye to length issues and linting headaches.

Features:

- [X] Loads prompts from a directory or json
- [ ] Insert text inside your prompt
- [X] Preprocess the inserted text

## How to Use

You can collect your prompts in a folder or in a json file.

### Folder-Based Prompt Management

Gather all your prompts into a folder, e.g. `folder_path`, saving them as `.txt` or `.md` files.

Then, simply run the following code:
    
    from wtPrompt.core import FolderPrompts

    my_prompts = FolderPrompts(prompt_folder='folder_path')

    # Now the following will return your prompt in .str format
    my_prompts.prompt_name
    my_prompts('prompt_name')

Where the prompt name is given by the file name, e.g., `hello.txt` can be loaded as `hello`.

### JSON-Based Prompt Management

Another option is to store your prompts in a .json file dictionary, of the kind:

    {
        'prompt name' : 'prompt content',
        ...
    }

This can be used in a similar fashion:

    from wtPrompt.core import FolderPrompts
    
    my_prompts = JsonPrompts(prompt_file='path_to_json.json')

    my_prompts.prompt_name
    my_prompts('prompt_name')

Note: the JSON will be validated
