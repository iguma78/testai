# TestAI SDK Documentation

Welcome to the TestAI SDK documentation. This SDK provides utilities for monitoring and recording OpenAI API calls in Python applications.

## Contents

- [Installation](installation.md)
- [Quick Start](quickstart.md)
- [API Reference](api.md)
- [Examples](examples.md)
- [Contributing](contributing.md)

## Overview

TestAI SDK allows you to monitor OpenAI API calls with detailed logging, capture request details, response metrics, and performance data. It automatically sends API call data to a central collection point. The SDK is designed to be easy to integrate with existing code through context managers with minimal overhead.

## Basic Example

```python
import os
import openai
from testai_sdk import result_ai_cm

# Set up OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Use the context manager to monitor OpenAI API calls
with result_ai_cm("classification_task", user_id="user123"):
    # Make an OpenAI API call - it will be monitored automatically
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Classify this text as positive or negative: 'I love this product!'"}
        ]
    )
    # The API call will be monitored and data will be sent to the collection endpoint
```
