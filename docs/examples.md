# Examples

This page contains various examples of how to use TestAI SDK in different scenarios.

## Basic OpenAI API Monitoring

```python
import os
import openai
from testai_sdk import result_ai_cm

# Set up OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Use the context manager to monitor OpenAI API calls
with result_ai_cm("basic_chat"):
    # Make an OpenAI API call
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, world!"}
        ]
    )
    print(response.choices[0].message.content)
```

## Adding User Information

```python
import openai
from testai_sdk import result_ai_cm

# Add user information to the monitoring
with result_ai_cm("user_query", user_id="user123", session_id="session456"):
    # Make an OpenAI API call
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What's the weather like today?"}
        ]
    )
    print(response.choices[0].message.content)
```

## Monitoring Different Task Types

```python
import openai
from testai_sdk import result_ai_cm

# Monitor a classification task
with result_ai_cm("classification", task_type="sentiment_analysis", dataset="customer_reviews"):
    # Make an OpenAI API call for classification
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a sentiment analysis assistant."},
            {"role": "user", "content": "Classify this review as positive or negative: 'I love this product!'"}
        ]
    )
    print(response.choices[0].message.content)

# Monitor a generation task
with result_ai_cm("generation", task_type="content_creation", content_type="blog_post"):
    # Make an OpenAI API call for generation
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a content creation assistant."},
            {"role": "user", "content": "Write a short blog post about artificial intelligence."}
        ]
    )
    print(response.choices[0].message.content)
```

## Adding Detailed Metadata

```python
import openai
from testai_sdk import result_ai_cm

# Add detailed metadata to the monitoring
with result_ai_cm(
    "detailed_task",
    user_id="user123",
    session_id="session456",
    environment="production",
    version="1.0.0",
    region="us-east-1",
    device="mobile",
    platform="ios",
    timestamp="2025-05-08T12:34:56Z"
):
    # Make an OpenAI API call
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Tell me a joke."}
        ]
    )
    print(response.choices[0].message.content)
```
