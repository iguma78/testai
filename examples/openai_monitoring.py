
import os
import openai
from result_ai_sdk import result_ai_cm

# Set up OpenAI API key
# In a real application, you would set this through environment variables
openai.api_key = os.environ.get("OPENAI_API_KEY", "your-api-key")

def main():
    # Example 1: Basic OpenAI API call without monitoring
    print("Example 1: Basic OpenAI API call without monitoring")
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, world!"}
        ]
    )
    print(f"Response: {response.choices[0].message.content}")
    print("=" * 40)

    # Example 2: Using the context manager to monitor the API call
    print("Example 2: Using the context manager to monitor the API call")
    with result_ai_cm("greeting_task", user_id="test_user", environment="development"):
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Tell me a joke."}
            ]
        )
        print(f"Response: {response.choices[0].message.content}")
    print("=" * 40)

    # Example 3: Verify that the original function is restored
    print("Example 3: After context manager")
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What's the weather like?"}
        ]
    )
    print(f"Response: {response.choices[0].message.content}")
    print("=" * 40)

    # Example 4: Using the context manager with additional metadata
    print("Example 4: Using the context manager with additional metadata")
    with result_ai_cm(
        "classification_task",
        user_id="test_user",
        environment="development",
        task_type="classification",
        priority="high"
    ):
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Classify this text as positive or negative: 'I love this product!'"}
            ]
        )
        print(f"Response: {response.choices[0].message.content}")
    print("=" * 40)


if __name__ == "__main__":
    main()
