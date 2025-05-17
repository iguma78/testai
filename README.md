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

client = openai.OpenAI(api_key="OPENAI_API_KEY")

# Use the context manager to monitor OpenAI API calls
prompt_template = "classify the following tweet to positive or negative: {tweet}"
tweet = "I love u all"
with result_ai(task_name="tweet classification",
               prompt_template=prompt_template,
               tweet=tweet,
               metadata={"lang": "en"}):
    # Make an API call - it will be monitored automatically
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt_template.format(tweet=tweet)}
        ]
    )
```

### Important Note on Prompt Templates

When using the `result_ai` context manager, you must provide values for all placeholders that appear in your prompt template. In the example above:

1. The prompt template contains `{tweet}` as a placeholder
2. The context manager initialization includes `tweet="I love u all"` which provides the value for this placeholder
3. Any placeholder in your template string should be passed as a keyword argument with the same name

If you have multiple placeholders (e.g., `"Translate {text} from {source_lang} to {target_lang}"`), you should provide all three variables (`text`, `source_lang`, and `target_lang`) as keyword arguments to the context manager.

For any additional arguments that are not placeholders in your prompt template but that you want to track, you can include them in the `metadata` dictionary:

```python
with result_ai(task_name="translation service",
               prompt_template="Translate {text} to {target_lang}",
               text="Hello world",
               target_lang="Spanish",
               metadata={
                   "user_id": "user_123",
                   "request_source": "mobile_app",
                   "priority": "high"
               }):
    # Your API call here
```

This allows you to track contextual information alongside your prompt while keeping the template variables separate.

## Environment Variables

The SDK uses the following environment variables:

- `RESULTAI_API_KEY`: Your ResultAI API key for authenticating requests to the monitoring service. If not set, monitoring will be disabled.
- `RESULTAI_ENABLED`: Set to "false" to disable monitoring globally, regardless of other settings. Not specifying, or setting to "true" will enable monitoring (subject to API key availability).

Example:
```bash
# Enable monitoring with your API key
export RESULTAI_API_KEY="your-api-key-here"

# Disable monitoring temporarily
export RESULTAI_ENABLED="false"
```

## License

MIT
