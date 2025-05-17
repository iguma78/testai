"""
Unit tests for the TestAI SDK functionality.
"""

import os
import datetime
import unittest.mock as mock
from typing import Any, Dict

import wrapt
import openai
import pytest

from result_ai_sdk import result_ai
from result_ai_sdk.patch import SUPPORTED_MODULES_TO_PATCH


def get_func(module_name_to_patch: str, func_name_to_patch: str):
    (parent, attribute, original) = wrapt.resolve_path(module_name_to_patch, func_name_to_patch)
    return original


@pytest.fixture(scope="module")
def original_funcs():
    """Fixture to store original functions before patching."""
    funcs = {}
    for module_obj in SUPPORTED_MODULES_TO_PATCH:
        funcs[(module_obj.module_name_to_patch, module_obj.func_name_to_patch)] = get_func(
            module_obj.module_name_to_patch, module_obj.func_name_to_patch
        )
    return funcs


def create_client_and_make_call(module_obj):
    """Create appropriate client and make API call based on module type."""
    if "openai" in module_obj.module_name_to_patch:
        client = openai.OpenAI(api_key="")
        # Make an OpenAI API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant.",
                },
                {"role": "user", "content": "Hello, world!"},
            ],
        )
        return response
    elif "langchain" in module_obj.module_name_to_patch:
        # Mock LangChain model
        from langchain.chat_models import init_chat_model
        from langchain_core.messages import HumanMessage, SystemMessage

        m = init_chat_model(
            model="anthropic.claude-3-7-sonnet-20250219-v1:0",
            model_provider="bedrock_converse",
            region_name="us-east-1",
        )

        # Convert dict messages to langchain message objects
        messages = [SystemMessage(content="You are a helpful assistant."), HumanMessage(content="Hello, world!")]

        response = m.generate(messages=messages)
        return response
    else:
        pytest.fail(f"Unsupported module: {module_obj.module_name_to_patch}")


def verify_expected_data(data: Dict[str, Any], module_obj):
    """Verify the expected data based on module type."""
    # Check top-level fields
    assert data["task_name"] == "test_task"
    assert data["prompt_template"] == "{param} there"
    assert data["metadata"] == {}
    assert data["user_input_args"] == {"param": "value"}
    assert data["response_data"]["success"]

    assert data["response_data"]["latency"] > 0
    assert data["response_data"]["latency"] < 0.001

    assert isinstance(data["request_data"]["llm_call_instance"], dict)
    for key in data["request_data"]["llm_call_instance"].keys():
        assert isinstance(key, str)

    timestamp = datetime.datetime.fromisoformat(data["timestamp"])
    assert datetime.datetime.now() - datetime.timedelta(seconds=10) <= timestamp
    assert timestamp <= datetime.datetime.now()

    # Check request_data fields based on module type
    if "openai" in module_obj.module_name_to_patch:
        # Check only specific fields in request_data rather than the whole dict
        assert data["function_patched"] == "Completions.create"
        assert data["module_patched"] == "openai.resources.chat.completions"
        assert data["root_module_name_patched"] == "openai"

        # Verify request data
        assert data["request_data"]["llm_call_instance_type"] == get_func(
            "openai.resources.chat.completions", "Completions"
        )
        assert data["request_data"]["llm_call_instance_type_name"] == "Completions"

        # Verify LLM call arguments
        assert data["request_data"]["llm_call_arguments"]["model"] == "gpt-3.5-turbo"
        assert data["request_data"]["llm_call_arguments"]["messages"] == [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, world!"},
        ]

    elif "langchain" in module_obj.module_name_to_patch:
        # Check only specific fields in request_data rather than the whole dict
        assert data["function_patched"] == "BaseChatModel.generate"
        assert data["module_patched"] == "langchain_core.language_models"
        assert data["root_module_name_patched"] == "langchain_core"

        # Verify request data
        from langchain_aws import ChatBedrockConverse

        assert data["request_data"]["llm_call_instance"]["model_id"] == "anthropic.claude-3-7-sonnet-20250219-v1:0"
        assert data["request_data"]["llm_call_instance_type"] == ChatBedrockConverse
        assert data["request_data"]["llm_call_instance_type_name"] == "ChatBedrockConverse"

        # For LangChain, we're only checking that the messages entry exists since the format changes
        assert "messages" in data["request_data"]["llm_call_arguments"]


@pytest.mark.parametrize(
    "module_obj, enabled, enabled_env",
    [
        (module, enabled, enabled_env)
        for module, enabled, enabled_env in zip(
            SUPPORTED_MODULES_TO_PATCH, [True, False], ["True", "False", "false", "true", "bla", None]
        )
    ],
)
def test_module_monitoring_and_restoration(module_obj, enabled, enabled_env, monkeypatch, original_funcs):
    """Test module monitoring and restoration after context manager exits."""

    mock_add_to_queue = mock.MagicMock()
    monkeypatch.setattr("result_ai_sdk.patch.add_to_queue", mock_add_to_queue)

    # Mock the API function
    mock_model = mock.create_autospec(original_funcs[(module_obj.module_name_to_patch, module_obj.func_name_to_patch)])
    mock_model_response = mock.MagicMock()
    mock_model.return_value = mock_model_response
    monkeypatch.setattr(f"{module_obj.module_name_to_patch}.{module_obj.func_name_to_patch}", mock_model)

    os.environ["RESULTAI_API_KEY"] = "test_api_key"

    # Set or unset RESULTAI_ENABLED environment variable
    if enabled_env is None:
        monkeypatch.delenv("RESULTAI_ENABLED", raising=False)
    else:
        os.environ["RESULTAI_ENABLED"] = enabled_env

    # Calculate if monitoring should actually be enabled based on both parameters
    should_monitor = enabled and (enabled_env.lower() != "false" if enabled_env is not None else True)

    # Use the context manager
    with result_ai(task_name="test_task", prompt_template="{param} there", param="value", enabled=enabled):
        # The function should be wrapped
        current_func = get_func(
            module_name_to_patch=module_obj.module_name_to_patch,
            func_name_to_patch=module_obj.func_name_to_patch,
        )

        if should_monitor:
            assert isinstance(current_func, wrapt.FunctionWrapper)
            assert current_func == mock_model
            assert current_func is not mock_model
            assert current_func.__wrapped__ is mock_model
            assert "result_ai_wrapper" in current_func._self_wrapper.__name__
        else:
            assert not isinstance(current_func, wrapt.ObjectProxy)
            assert current_func is mock_model

        # Make an API call appropriate for the module
        response = create_client_and_make_call(module_obj)

        # Check the response
        assert response is mock_model_response

    # Check that the original function was called
    mock_model.assert_called_once()

    if should_monitor:
        # Check that add_to_queue was called
        mock_add_to_queue.assert_called_once()
        # Verify expected data for this module
        data = mock_add_to_queue.call_args[0][0]
        verify_expected_data(data, module_obj)
    else:
        mock_add_to_queue.assert_not_called()

    # After the context manager exits, the function should be restored
    current_func = get_func(module_obj.module_name_to_patch, module_obj.func_name_to_patch)
    assert not isinstance(current_func, wrapt.ObjectProxy)
    assert current_func is mock_model
