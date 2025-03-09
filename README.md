# 🤌 wtprompt: What the Prompt?

*wtprompt* is a lightweight, no-nonsense library designed to help you manage your LLM prompts efficiently.

Tired of cluttering your code with blocks of text? *wtprompt* keeps your code clean by loading prompts from files or JSON. Say goodbye to length issues and linting headaches.

## 🚀 Why wtprompt?

- ✅ **Zero bloat** – Need just prompts? No need for a full MLOps library.  
- ✅ **Jinja support** – Use powerful templating syntax for dynamic prompts.  
- ✅ **Markdown-friendly** – Ready for OpenAI-style Markdown prompting.  
- ✅ **Folder & JSON support** – Load prompts from structured files or JSON.  
- ✅ **Prompt hashing** – Track prompts with unique identifiers.  
- ✅ **Built-in preprocessing** – Clean input text before inserting it into prompts.  

---

## 🛠 Installation

```bash
pip install wtprompt
```

---

## 🔥 Quickstart

### 1️⃣ Load prompts from a folder  

Store your prompts as `.txt` or `.md` files in a folder:

```
prompts/
  ├── fill_test.txt  # "Today is {{ day }} in the month of {{ this_month }}."
  ├── hello.txt
  ├── subfolder/
  │   ├── question.md
```

Then, load them:

```python
from wtprompt import FolderPrompts

base_prompts = FolderPrompts("prompts")

# Retrieve a prompt
prompt = base_prompts.hello  # Loads "hello.txt"
prompt = base_prompts.subfolder.question  # Loads "subfolder/question.md"
```

### 2️⃣ Fill in values  

Now you can **directly fill prompts** using `fill_prompt`:

```python
filled_prompt = base_prompts.fill_prompt("fill_test", {"day": "Monday", "this_month": "August"})
print(filled_prompt)
```

➡️ **Output:**  
`"Today is Monday in the month of August."`

For simpler cases, use `fill_list`:

```python
filled_prompt = base_prompts.fill_list("fill_test", ["Monday", "August"])
```

> **Tip:** `fill_list` is faster for basic substitutions, but Jinja allows more flexibility.

---

## 📂 Folder-Based Prompt Management

`FolderPrompts` helps organize and manage prompts with structured storage.

### Load prompts dynamically  

```python
my_prompts = FolderPrompts("prompts")

# Direct attribute access
prompt_text = my_prompts.prompt_name
prompt_text = my_prompts.subfolder.prompt_name
```

### Save and load prompt reports  

```python
my_prompts.save_prompt_report("report.json")
my_prompts.load_from_prompt_report("report.json", strict=True)
```

> **Strict mode** ensures that prompt hashes match.

---

## 📄 JSON-Based Prompt Loading

Store prompts in a JSON file:

```json
{
    "greeting": "Hello, {{ name }}!",
    "farewell": "Goodbye, {{ name }}."
}
```

Load and use them:

```python
from wtprompt import JsonPrompts

prompts = JsonPrompts("prompts.json")
prompt = prompts.greeting  # Or prompts("greeting")
```

> **Note:** JSON loading is not lazy. Use `validate=True` to check for errors.

---

## 📝 Define Prompts in Code

For quick prototyping, define prompts manually:

```python
from wtprompt import PromptLoader

prompts = PromptLoader()
prompts.add_prompt("greeting", "Hello, {{ name }}!")

# Retrieve the prompt and its hash
text, hash_id = prompts.get_prompt("greeting", get_hash=True)
```

---

## 🔧 Text Preprocessing

Raw text can be messy. Use `TextPreprocessor` for basic cleaning:

```python
from wtprompt.utils.preprocessor import TextPreprocessor

preprocessor = TextPreprocessor()

is_valid, cleaned_text = preprocessor.preprocess("   Hello!   ")
assert is_valid  # True
```

Customizable settings include:

- **Whitespace handling**: Trim spaces, limit consecutive spaces.
- **Validation**: Ensure text isn’t empty or gibberish.
- **Truncation**: Limit max length.
- **Character filtering**: Enforce ASCII, Unicode normalization.

Example:

```python
def build_prompt(prompts, preprocessor, context, question):
    is_ok, context = preprocessor.preprocess(context)
    assert is_ok, "ERROR: Invalid context"
    return base_prompts.fill_list("prompt_name", [context, question])
```

---

## TL;DR

✔️ Store prompts in **folders** or **JSON**.  
✔️ Use **Jinja templating** to insert dynamic values.  
✔️ Apply **preprocessing** for cleaner input.  

---

### 📜 License & Contributions

Licensed under **MIT**. Contributions are welcome!