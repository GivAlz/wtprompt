from setuptools import setup, find_packages

setup(
    name='wtprompt',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pydantic~=2.8.2',
    ],
    python_requires='>=3.8',
    author='Giovanni Alzetta',
    author_email='giovannialzetta@gmail.com',
    description='A lightweight, no-nonsense library for managing your LLM prompts.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/GivAlz/wtPrompt',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
