"""
Unit tests for the TestAI SDK functionality.
"""

import unittest
import unittest.mock as mock
import openai
import wrapt
from result_ai_sdk import result_ai_cm
from result_ai_sdk.queue import add_to_queue


class TestResultAiCm(unittest.TestCase):
    """Test cases for the result_ai_cm context manager."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a mock for the OpenAI API
        self.original_create = openai.resources.chat.completions.Completions.create
        
        # Create a mock response
        self.mock_response = mock.MagicMock()
        self.mock_response.choices = [mock.MagicMock()]
        self.mock_response.choices[0].message.content = "Test response"
        self.mock_response.usage = mock.MagicMock()
        self.mock_response.usage.total_tokens = 100
        self.mock_response.usage.completion_tokens = 50
        self.mock_response.usage.prompt_tokens = 50
        
        # Mock the add_to_queue function
        self.original_add_to_queue = add_to_queue
        self.queue_items = []
        
    def tearDown(self):
        """Clean up after the test."""
        # Restore the original OpenAI API
        openai.resources.chat.completions.Completions.create = self.original_create
        # Restore the original add_to_queue function
        globals()['add_to_queue'] = self.original_add_to_queue
    
    @mock.patch('result_ai_sdk.queue.add_to_queue')
    def test_openai_monitoring(self, mock_add_to_queue):
        """Test that OpenAI API calls are properly monitored."""
        # Mock the OpenAI API
        mock_create = mock.MagicMock(return_value=self.mock_response)
        openai.resources.chat.completions.Completions.create = mock_create
        
        # Create a context manager
        with result_ai_cm("test_task", param="value"):
            # The function should be wrapped
            self.assertIsInstance(openai.resources.chat.completions.Completions.create, wrapt.ObjectProxy)
            
            # Make an OpenAI API call
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello, world!"}
                ]
            )
            
            # Check the response
            self.assertEqual(response.choices[0].message.content, "Test response")
        
        # Check that add_to_queue was called
        mock_add_to_queue.assert_called_once()
        
        # Check the data passed to add_to_queue
        args, _ = mock_add_to_queue.call_args
        data = args[0]
        
        # Verify the structure of the data
        self.assertEqual(data["task"], "test_task")
        self.assertEqual(data["user_id"], "1897ce6d-5694-41ce-a75d-8ea9e4dc81b4")
        self.assertIn("request_data", data)
        self.assertIn("response_data", data)
        
        # Verify request data
        self.assertEqual(data["request_data"]["type"], "openai_request")
        self.assertIn("timestamp", data["request_data"])
        self.assertEqual(data["request_data"]["input_args"], {"param": "value"})
        
        # Verify response data
        self.assertTrue(data["response_data"]["success"])
        self.assertEqual(data["response_data"]["total_tokens"], 100)
        self.assertEqual(data["response_data"]["completion"], "Test response")
    
    @mock.patch('result_ai_sdk.queue.add_to_queue')
    def test_context_manager_restoration(self, mock_add_to_queue):
        """Test that the original OpenAI API is restored after the context manager exits."""
        # Save the original function
        original_func = openai.resources.chat.completions.Completions.create
        
        # Mock the OpenAI API
        mock_create = mock.MagicMock(return_value=self.mock_response)
        openai.resources.chat.completions.Completions.create = mock_create
        
        # Use the context manager
        with result_ai_cm("test_task"):
            # The function should be wrapped
            self.assertIsInstance(openai.resources.chat.completions.Completions.create, wrapt.ObjectProxy)
            self.assertNotEqual(openai.resources.chat.completions.Completions.create, original_func)
            
            # Make an API call
            openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}]
            )
        
        # After the context manager exits, the function should be restored
        self.assertEqual(openai.resources.chat.completions.Completions.create, original_func)
        self.assertNotIsInstance(openai.resources.chat.completions.Completions.create, wrapt.ObjectProxy)


if __name__ == "__main__":
    unittest.main() 