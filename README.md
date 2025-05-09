# ResultAI SDK

A Python SDK for monitoring and recording LLM API calls in Python applications.

## Installation

```bash
pip install git+https://github.com/iguma78/testai.git
```

## Features

- Monitor LLM API calls with just one line of code
- Capture request details, response metrics, and performance data
- Easily integrate with existing code through context managers

## Quick Start

```python
import openai
from result_ai_sdk import result_ai

# Set up OpenAI client
client = openai.OpenAI(api_key="OPENAI_API_KEY)

# Use the context manager to monitor OpenAI API calls
prompt_template = "classify the following tweet: {tweet} to positive or negative"
tweet = "I love u all"
with result_ai(task_name"tweet classification",
               prompt_template=prompt_template,
               tweet=tweet):
    # Make an OpenAI API call - it will be monitored automatically
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt_template.format(tweet=tweet)}
        ]
    )
```

## License

MIT
