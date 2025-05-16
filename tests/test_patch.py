"""
Unit tests for the TestAI SDK functionality.
"""

import os
import datetime
import unittest
import unittest.mock as mock

import wrapt
import openai
from langchain.chat_models import init_chat_model

from result_ai_sdk import result_ai
from result_ai_sdk.patch import SUPPORTED_MODULES_TO_PATCH, _patch_func


def get_func(module_name_to_patch: str, func_name_to_patch: str):
    (parent, attribute, original) = wrapt.resolve_path(module_name_to_patch, func_name_to_patch)
    return original


class TestResultAiCm(unittest.TestCase):
    """Test cases for the result_ai_cm context manager."""

    @classmethod
    def setUpClass(cls):
        cls.original_funcs = {}
        for module_obj in SUPPORTED_MODULES_TO_PATCH:
            cls.original_funcs[(module_obj.module_name_to_patch, module_obj.func_name_to_patch)] = get_func(
                module_obj.module_name_to_patch, module_obj.func_name_to_patch
            )

    def setUp(self):
        self.maxDiff = None
        self.mock_create_response = mock.MagicMock()

    def _create_client_and_make_call(self, module_obj):
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
            m = init_chat_model(
                model="anthropic.claude-3-7-sonnet-20250219-v1:0",
                model_provider="bedrock_converse",
                region_name="us-east-1",
            )
            response = m.generate(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant.",
                    },
                    {"role": "user", "content": "Hello, world!"},
                ]
            )
            return response
        else:
            self.fail(f"Unsupported module: {module_obj.module_name_to_patch}")

    def _verify_expected_data(self, data, module_obj):
        """Verify the expected data based on module type."""
        # Check top-level fields
        self.assertEqual(data["task_name"], "test_task")
        self.assertEqual(data["prompt_template"], "{param} there")
        self.assertEqual(data["metadata"], {})
        self.assertEqual(data["user_input_args"], {"param": "value"})
        self.assertTrue(data["response_data"]["success"])

        self.assertGreater(data["response_data"]["latency"], 0)
        self.assertLess(data["response_data"]["latency"], 0.001)

        self.assertIsInstance(data["request_data"]["llm_call_instance"], dict)
        for key in data["request_data"]["llm_call_instance"].keys():
            self.assertIsInstance(key, str)

        self.assertTrue(
            datetime.datetime.now() - datetime.timedelta(seconds=10)
            <= datetime.datetime.fromisoformat(data["timestamp"])
        )
        self.assertTrue(datetime.datetime.fromisoformat(data["timestamp"]) <= datetime.datetime.now())

        # Check request_data fields based on module type
        if "openai" in module_obj.module_name_to_patch:
            # Check only specific fields in request_data rather than the whole dict
            self.assertEqual(data["function_patched"], "Completions.create")
            self.assertEqual(data["module_patched"], "openai.resources.chat.completions")
            self.assertEqual(data["root_module_name_patched"], "openai")

            # Verify request data
            self.assertEqual(
                data["request_data"]["llm_call_instance_type"],
                second=get_func("openai.resources.chat.completions", "Completions"),
            )
            self.assertEqual(data["request_data"]["llm_call_instance_type_name"], "Completions")

            # Verify LLM call arguments
            self.assertEqual(data["request_data"]["llm_call_arguments"]["model"], "gpt-3.5-turbo")
            self.assertEqual(
                data["request_data"]["llm_call_arguments"]["messages"],
                [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello, world!"},
                ],
            )

            # Verify response data
            self.assertIs(data["response_data"]["response"], self.mock_create_response.dict())

        elif "langchain" in module_obj.module_name_to_patch:
            # Check only specific fields in request_data rather than the whole dict
            self.assertEqual(data["function_patched"], "BaseChatModel.generate")
            self.assertEqual(data["module_patched"], "langchain_core.language_models")
            self.assertEqual(data["root_module_name_patched"], "langchain_core")

            # Verify request data
            self.assertEqual(
                data["request_data"]["llm_call_instance"]["model_id"], "anthropic.claude-3-7-sonnet-20250219-v1:0"
            )
            from langchain_aws import ChatBedrockConverse

            self.assertEqual(data["request_data"]["llm_call_instance_type"], second=ChatBedrockConverse)
            self.assertEqual(data["request_data"]["llm_call_instance_type_name"], "ChatBedrockConverse")

            # Verify LLM call arguments
            self.assertEqual(
                data["request_data"]["llm_call_arguments"]["messages"],
                [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello, world!"},
                ],
            )

            # Verify response data
            self.assertIs(data["response_data"]["response"], self.mock_create_response.dict())

    @mock.patch("result_ai_sdk.patch.add_to_queue")
    def test_module_monitoring_and_restoration(self, mock_add_to_queue):
        """Test module monitoring and restoration after context manager exits."""
        for module_obj in SUPPORTED_MODULES_TO_PATCH:
            with self.subTest(
                module_name=module_obj.module_name_to_patch,
                func_name=module_obj.func_name_to_patch,
            ):
                mock_add_to_queue.reset_mock()

                # Mock the API
                mock_create = mock.create_autospec(
                    TestResultAiCm.original_funcs[(module_obj.module_name_to_patch, module_obj.func_name_to_patch)]
                )
                mock_create.return_value = self.mock_create_response

                _patch_func(
                    module_name_to_patch=module_obj.module_name_to_patch,
                    func_name_to_patch=module_obj.func_name_to_patch,
                    new_func=mock_create,
                )
                os.environ["RESULTAI_API_KEY"] = "test_api_key"

                # Use the context manager
                with result_ai(task_name="test_task", prompt_template="{param} there", param="value"):
                    # The function should be wrapped
                    current_func = get_func(
                        module_name_to_patch=module_obj.module_name_to_patch,
                        func_name_to_patch=module_obj.func_name_to_patch,
                    )
                    self.assertIsInstance(current_func, wrapt.FunctionWrapper)
                    self.assertEqual(current_func, mock_create)
                    self.assertIsNot(current_func, mock_create)
                    self.assertIs(current_func.__wrapped__, mock_create)
                    self.assertIn("result_ai_wrapper", current_func._self_wrapper.__name__)

                    # Make an API call appropriate for the module
                    response = self._create_client_and_make_call(module_obj)

                    # Check the response
                    self.assertIs(response, self.mock_create_response)

                # Check that the original function was called
                mock_create.assert_called_once()

                # Check that add_to_queue was called
                mock_add_to_queue.assert_called_once()

                # Verify the data sent to the queue
                data = mock_add_to_queue.call_args[0][0]
                # print(data)

                # Verify expected data for this module
                self._verify_expected_data(data, module_obj)

                # After the context manager exits, the function should be restored
                current_func = get_func(module_obj.module_name_to_patch, module_obj.func_name_to_patch)
                self.assertNotIsInstance(current_func, wrapt.ObjectProxy)
                self.assertIs(current_func, mock_create)


if __name__ == "__main__":
    unittest.main()
