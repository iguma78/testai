# TestAI SDK

A Python SDK for monitoring and recording OpenAI API calls in Python applications.

## Installation

```bash
pip install testai-sdk
```

## Features

- Monitor OpenAI API calls with detailed logging
- Capture request details, response metrics, and performance data
- Automatically send API call data to a central collection point
- Easily integrate with existing code through context managers
- Minimal overhead and simple API

## Quick Start

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

## Advanced Usage

### Adding Custom Metadata

```python
import openai
from testai_sdk import result_ai_cm

# Add custom metadata to the monitored API calls
with result_ai_cm(
    "sentiment_analysis",
    user_id="user123",
    environment="production",
    dataset="customer_reviews",
    model_version="v1.0"
):
    # Make an OpenAI API call
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a sentiment analysis assistant."},
            {"role": "user", "content": "Analyze the sentiment: 'The service was excellent!'"}
        ]
    )
    # The API call will be monitored with the additional metadata
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/teleprompt-sdk.git
cd teleprompt-sdk

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```
#Create a Local Package Index:
##You can build the package and install it from a local directory:
### In this package directory
python setup.py sdist bdist_wheel
### Then in your other project
pip install /path/to/this/package/dist/your_package_name-version.tar.gz

### Running Tests

```bash
pytest
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
