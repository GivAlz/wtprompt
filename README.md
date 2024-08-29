# 🤌 wtprompt (What the Prompt?)

*wtprompt*: a lightweight, no-nonsense library for managing your LLM prompts.

Tired of cluttering your code with blocks of text? *wtprompt* lets you keep your code clean by loading prompts
from text files. Say goodbye to length issues and linting headaches.

## Why wtprompt?

- ✅ **Lightweight, zero bloat**: need to just work with prompts? Use this instead of a full MLOps library
- ✅ **Jinja syntax**: Leverage the powerful Jinja syntax, already used by *haystack* and other libraries
- ✅ **Markdown-friendly**: OpenAI is popularizing Markdown as a prompt language, *wtprompt* is ready for that!
- ✅ **Easy Prompt Managament**: Instantly load prompts from a directory (and its subdirectories) or JSON file
- ✅ **Dynamic Prompts**: Seamlessly insert text into your prompts at runtime
- ✅ **Built-in Preprocessing** Access straightforward, ready-to-use preprocessing for your text

### Folder-Based Prompt Loading

Gather all your prompts into a folder, e.g. `folder_path`, saving them as `.txt` or `.md` files. You can organize them
into subfolders, and they will be loaded according to the original folder structure.

Then, simply run the following code:

```python
from wtprompt.core import FolderPrompts

my_prompts = FolderPrompts(prompt_folder='folder_path')

# Now the following commands will return your prompt as a str variable
prompt = my_prompts.prompt_name
# Note, nested calls like `my_prompts.subfolder.prompt_name` won't work!

prompt = my_prompts('prompt_name')
prompt = my_prompts('subfolder/prompt_name')
```

Where the prompt name is given by the file name, e.g., `hello.txt` can be loaded as `hello`.

Remark:

Folder-based loading is lazy: call the `.load()` method to load the whole folder structure.

### JSON-Based Prompt Loading

Another option is to store your prompts in a .json file dictionary, of the kind:

    {
        'prompt name' : 'prompt content',
        ...
    }

This can be used in a similar fashion:

```python
from wtprompt.core import JsonPrompts

my_prompts = JsonPrompts(prompt_file='path_to_json.json')

my_prompts.prompt_name
my_prompts('prompt_name')
```


Remark:

- To speed up the loading times the JSON is not validated: pass the flag `validate=True` or use the function `validate_json` to check your json file.
- Currently lazy loading is not supported for JSON files.

### Prompts in-Code

It is possible to initialise an empty `PromptLoader` class:

```python
my_prompts = PromptLoader()
```

And then add prompts as follows:

```python
my_prompts.add_prompt(prompt_name, prompt_text)
```

where prompt_name and prompt_text are string variables.

## Fill in Values

One of the primary reasons for embedding prompts directly within the code
is to streamline the process of populating values.

This situation is typical, for example, of a Retrieval-Augmented Generation (RAG) system,
where the prompt often follows a structure of this kind:

<div class="code-title">Prompt Example</div>

```
Basing your answer only on the following context

# Context
--- variable context ---

Answer the following question

# Question:
--- variable question ---
```

*wtprompt* allows to easily handle this use case. There are two main approaches:

- `fill_list`: a function which will substitute some values in order, quicker to use for simple substitutions: not necessarily compatible with jinja syntax!
- `PromptGenerator`: a class which, through the method `fill_prompt`,
- allows to use the [Jinja](https://jinja.palletsprojects.com/en/3.1.x/) templates.

For example by writing the previous prompt as follows:

```
Basing your answer only on the following context

# Context
{{context}}

Answer the following question

# Question:
{{question}}
```

it is possible to make the proper substitutions in one of the following ways:

```python
p_gen = PromptGenerator()
# Using a dictionary to make the substitutions
filled_in_prompt = p_gen.fill_prompt(wtprompt.prompt_name, {'question': '...question here...',
                                               'context': '...context here...'})

# Using a list to make the substitutions
# In this case the order of the variables and the placeholders has to be the same
filled_in_prompt = fill_list(wtprompt.prompt_name, ['...context here...', '...question here...'])
```

Remarks:
- Jinja can be flexible and powerful, which is why it is used by many projects (for instance Haystack). See Jinja's documentation for more details.
- To minimize the likelihood of errors, it is recommended to use `fill_list` when there are only a few substitutions.
- For `fill_list`, nested substitutions are not allowed.

## Text Preprocessing

The text that is added, especially if automatically selected or typed by a user, is potentially
messy.

For this reason wrPrompt offers a basic tool `TextPreprocessor`, that does some basic preprocessing.

The `preprocessor` method returns a `bool` and a `str`; if the `bool` is `False`
the preprocessing stopped half-way because of some property not being satisfied, if it is
`True` then the `str` is the processed string.

The following  variables control the default functionalities of the class:


- **do_strip (bool)**: If True removes leading and trailing whitespace.
- **check_empty (bool)**: Verifies if the text is non-empty.
- **check_letters (bool)**: If True compares the number of letters to the total number of characters.
- **percentage_letters (float)**: If check_letters is True this is the minimum percentage of accepted letters.
- **spaces_only (bool)**: If true, replaces all whitespace characters with spaces.
- **max_consecutive_spaces (int)**: Limits consecutive spaces to a specified maximum.
- **text_truncate (bool)**: If True text can be truncated to a specified maximum length.
- **max_length (int)**: Max length of the processed text (to be used if text_truncate = True)
- **ascii_only (bool)**: If True removes non-ASCII characters.
- **text_normalize (str)**: Normalizes the text using a specified Unicode normalization form.
- **has_min_length (bool)**: Verifies if the text meets a minimum length requirement.
- **min_length (int)**: Min length of the processed text (to be used if has_min_length = True)

To continue the previous example, it is possible to perform a basic preprocessing in the following way:

```python
preprocessor = TextPreprocessor()

def build_prompt(my_prompts, preprocessor, context, question):
    is_okay, context = preprocessor.preprocess(context)
    assert is_okay, "ERROR: Invalid context"
    return my_prompts.fill_list("prompt_name", [context, question])
```


**Note** 💡 The preprocessing class performs basic steps by default. In a production environment, you may want to customize the pipeline or add specific steps to meet your requirements.

## TL;DR

- Organize your prompts by storing them in a folder or within a JSON file.
- Utilize a dictionary or list to dynamically modify the prompts during runtime.
- Apply the preprocessor to perform basic processing on the filler values before using the prompts.

### License

This software is distributed under the MIT License (see LICENSE for details).
You are free to use, modify, and distribute it as you wish; however, attribution is appreciated.
