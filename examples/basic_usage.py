"""
Basic usage example for the TestAI SDK.

This example demonstrates how to use the result_ai_cm context manager
to monitor OpenAI API calls.
"""

import os

import openai

from result_ai_sdk import result_ai

# Set up OpenAI API key
# In a real application, you would set this through environment variables
openai.api_key = os.environ.get("OPENAI_API_KEY", "your-api-key")

# Example 1: Basic OpenAI API call without monitoring
print("Example 1: Basic OpenAI API call without monitoring")
try:
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, world!"},
        ],
    )
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"Error making API call: {e}")
print("=" * 40)

# Example 2: Using the context manager to monitor the API call
print("Example 2: Using the context manager")
try:
    with result_ai("joke_task", category="humor"):
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Tell me a joke."},
            ],
        )
        print(f"Response: {response.choices[0].message.content}")
        # The API call will be monitored and data will be sent to the collection
        # endpoint
except Exception as e:
    print(f"Error making API call: {e}")
print("=" * 40)

# Example 3: Adding detailed metadata
print("Example 3: Adding detailed metadata")
try:
    with result_ai(
        "classification_task",
        user_id="test_user",
        environment="development",
        model_version="gpt-3.5-turbo",
        task_type="sentiment_analysis",
    ):
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a sentiment analysis assistant.",
                },
                {
                    "role": "user",
                    "content": "Classify this text as positive or negative: 'I love this product!'",
                },
            ],
        )
        print(f"Response: {response.choices[0].message.content}")
        # The API call will be monitored with additional metadata
except Exception as e:
    print(f"Error making API call: {e}")
print("=" * 40)

# Example 4: Multiple API calls in the same context
print("Example 4: Multiple API calls in the same context")
try:
    with result_ai("conversation_task", session_id="session123"):
        # First message
        response1 = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, how are you?"},
            ],
        )
        print(f"First response: {response1.choices[0].message.content}")

        # Second message (continuing the conversation)
        response2 = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, how are you?"},
                {"role": "assistant", "content": response1.choices[0].message.content},
                {"role": "user", "content": "What can you help me with today?"},
            ],
        )
        print(f"Second response: {response2.choices[0].message.content}")
        # Both API calls will be monitored in the same task context
except Exception as e:
    print(f"Error making API call: {e}")
print("=" * 40)
