# Installation Guide

## Requirements

TestAI SDK requires:

- Python 3.7 or later
- OpenAI Python SDK v1.0.0 or later
- Requests library v2.25.0 or later

## Installing from PyPI

The recommended way to install TestAI SDK is via pip:

```bash
pip install testai-sdk
```

## Installing from Source

You can also install the package directly from the source code:

```bash
git clone https://github.com/yourusername/testai-sdk.git
cd testai-sdk
pip install -e .
```

## Development Installation

If you want to contribute to the development of TestAI SDK, you can install the package in development mode:

```bash
git clone https://github.com/yourusername/testai-sdk.git
cd testai-sdk
pip install -e ".[dev]"
```

## Verifying Installation

You can verify that the installation was successful by importing the package in Python:

```python
import testai_sdk
print(testai_sdk.__version__)
```

This should print the version number of the installed package.

## OpenAI API Key Configuration

The TestAI SDK requires an OpenAI API key to function properly. You can set it in your environment:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or in your Python code:

```python
import openai
openai.api_key = "your-api-key-here"
```
