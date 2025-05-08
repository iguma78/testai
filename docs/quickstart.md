# Quick Start Guide

This guide will help you get started with TestAI SDK quickly.

## Installation

Install the package using pip:

```bash
pip install testai-sdk
```

## Requirements

The TestAI SDK requires:

- Python 3.7 or later
- OpenAI Python SDK v1.0.0 or later
- Requests library v2.25.0 or later

## Basic Usage

Here's a simple example of how to use the TestAI SDK to monitor OpenAI API calls:

```python
import os
import openai
from testai_sdk import result_ai_cm

# Set up OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Use the context manager to monitor OpenAI API calls
with result_ai_cm("classification_task"):
    # Make an OpenAI API call - it will be monitored automatically
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, world!"}
        ]
    )
    # The API call will be monitored and data will be sent to the collection endpoint
```

## Adding Metadata

You can add custom metadata to your API calls to provide additional context:

```python
import openai
from testai_sdk import result_ai_cm

# Add custom metadata to the monitored API calls
with result_ai_cm(
    "sentiment_analysis",
    user_id="user123",
    environment="production",
    dataset="customer_reviews"
):
    # Make an OpenAI API call
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a sentiment analysis assistant."},
            {"role": "user", "content": "Analyze the sentiment: 'The service was excellent!'"}
        ]
    )
```

## Next Steps

- Check out the [API Reference](api.md) for detailed information on all classes and methods
- See the [Examples](examples.md) for more advanced usage scenarios
- Learn how to [contribute](contributing.md) to the project
