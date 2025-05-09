"""
Unit tests for the TestAI SDK functionality.
"""

import datetime
import unittest
import unittest.mock as mock

import wrapt
import openai

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

    @mock.patch("result_ai_sdk.patch.add_to_queue")
    def test_openai_monitoring(self, mock_add_to_queue):
        for module_obj in SUPPORTED_MODULES_TO_PATCH:
            with self.subTest(
                module_name=module_obj.module_name_to_patch,
                func_name=module_obj.func_name_to_patch,
            ):
                mock_create = mock.create_autospec(
                    TestResultAiCm.original_funcs[(module_obj.module_name_to_patch, module_obj.func_name_to_patch)]
                )
                mock_create.return_value = self.mock_create_response

                _patch_func(
                    module_obj.module_name_to_patch,
                    module_obj.func_name_to_patch,
                    mock_create,
                )

                # Create a context manager
                with result_ai("test_task", param="value"):
                    # The function should be wrapped
                    self.assertIsInstance(
                        get_func(
                            module_obj.module_name_to_patch,
                            module_obj.func_name_to_patch,
                        ),
                        wrapt.FunctionWrapper,
                    )

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

                    # Check the response
                    self.assertIs(response.content, self.mock_create_response.content)

                mock_create.assert_called_once()
                # Check that add_to_queue was called
                mock_add_to_queue.assert_called_once()

                data = mock_add_to_queue.call_args[0][0]
                self.assertEqual(data.pop("function_patched"), module_obj.func_name_to_patch)
                self.assertEqual(data.pop("module_name_to_patch"), module_obj.module_name_to_patch)
                self.assertEqual(data.pop("root_module_name"), module_obj.root_module_name)
                datetime_in_data = datetime.datetime.fromisoformat(data.pop("timestamp"))
                self.assertTrue(datetime.datetime.now() - datetime.timedelta(seconds=10) <= datetime_in_data)
                self.assertTrue(datetime_in_data <= datetime.datetime.now())
                self.assertIs(data["response_data"].pop("response"), self.mock_create_response)
                self.assertAlmostEqual(data["response_data"].pop("latency"), 0.0, delta=0.001)

                expected_data = {
                    "user_id": "1897ce6d-5694-41ce-a75d-8ea9e4dc81b4",
                    "task_name": "test_task",
                    "user_input_args": {"param": "value"},
                    "request_data": {
                        "llm_call_arguments": {
                            "messages": [
                                {
                                    "role": "system",
                                    "content": "You are a helpful assistant.",
                                },
                                {"role": "user", "content": "Hello, world!"},
                            ],
                            "model": "gpt-3.5-turbo",
                        }
                    },
                    "response_data": {"success": True},
                }

                self.assertEqual(data, expected_data)

    @mock.patch("result_ai_sdk.patch.add_to_queue")
    def test_context_manager_restoration(self, mock_add_to_queue):
        for module_obj in SUPPORTED_MODULES_TO_PATCH:
            with self.subTest(
                module_name=module_obj.module_name_to_patch,
                func_name=module_obj.func_name_to_patch,
            ):
                """Test that the original OpenAI API is restored after the context manager exits."""
                # Mock the OpenAI API
                mock_create = mock.MagicMock(return_value=self.mock_create_response)
                _patch_func(
                    module_obj.module_name_to_patch,
                    module_obj.func_name_to_patch,
                    mock_create,
                )

                # Use the context manager
                with result_ai("test_task"):
                    # The function should be wrapped
                    current_func = get_func(module_obj.module_name_to_patch, module_obj.func_name_to_patch)
                    self.assertIsInstance(current_func, wrapt.FunctionWrapper)
                    self.assertEqual(current_func, mock_create)
                    self.assertIsNot(current_func, mock_create)
                    self.assertIs(current_func.__wrapped__, mock_create)
                    self.assertIn("result_ai_wrapper", current_func._self_wrapper.__name__)

                    client = openai.OpenAI(api_key="")
                    # Make an API call
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": "Hello"}],
                    )
                    self.assertIs(response.content, self.mock_create_response.content)

                mock_add_to_queue.assert_called_once()
                current_func = get_func(module_obj.module_name_to_patch, module_obj.func_name_to_patch)
                mock_create.assert_called_once()
                # After the context manager exits, the function should be restored
                self.assertNotIsInstance(current_func, wrapt.ObjectProxy)
                self.assertIs(current_func, mock_create)


if __name__ == "__main__":
    unittest.main()
