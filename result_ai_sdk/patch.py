"""
Patching functionality for the TestAI SDK.

This module provides the context manager for patching and monitoring API calls.
"""

import logging
import openai
from typing import Any, Dict

from .plugins.openai_wrapper import monitor_openai_call

logger = logging.getLogger("testai_sdk")

class result_ai_cm:
    """
    A context manager for monitoring OpenAI API calls.
    
    This class allows you to temporarily modify the behavior of the OpenAI API
    to monitor and record API calls, including request details, response metrics,
    and performance data.
    
    Args:
        task_name: A string identifier for the current task
        **kwargs: Additional keyword arguments to be stored with the API call data
    
    Example:
        >>> from testai_sdk import result_ai_cm
        >>> # Use the context manager
        >>> with result_ai_cm("classification_task", model="gpt-4"):
        ...     # Make an OpenAI API call
        ...     response = openai.chat.completions.create(
        ...         model="gpt-4",
        ...         messages=[{"role": "user", "content": "Hello, world!"}]
        ...     )
        ...     # The API call will be monitored and recorded
    """
    
    def __init__(self, task_name: str, **kwargs):
        """
        Initialize the context manager.
        
        Args:
            task_name: A string identifier for the current task
            **kwargs: Additional keyword arguments to be stored with the API call data
        """
        self.task_name = task_name
        self.input_args = kwargs
        self.old_func = None
        
    def __enter__(self):
        """
        Enter the context manager and patch the OpenAI API.
        
        Returns:
            The context manager instance
        """
        try:
            logger.info(f"Entering result_ai_cm context manager for task: {self.task_name}")
            try:
                self.old_func = openai.resources.chat.completions.Completions.create
            except Exception as e:
                logger.error(f"Error setting up result_ai_cm context manager: {str(e)}")
                
            openai.resources.chat.completions.Completions.create = monitor_openai_call(
                self.task_name,
                self.input_args,
                self.old_func
            )
            return self
        except Exception as e:
            logger.error(f"Error setting up result_ai_cm context manager: {str(e)}")
            raise

    def __exit__(self, exctype, excinst, exctb):
        """
        Exit the context manager and restore the original OpenAI API function.
        
        Args:
            exctype: Exception type if an exception was raised
            excinst: Exception value if an exception was raised
            exctb: Exception traceback if an exception was raised
        """
        try:
            logger.info(f"Exiting result_ai_cm context manager for task: {self.task_name}")
            openai.resources.chat.completions.Completions.create = self.old_func
            self.old_func = None
            if exctype:
                logger.error(f"Exception occurred in result_ai_cm context: {exctype.__name__}: {excinst}")
        except Exception as e:
            logger.error(f"Error in __exit__ of result_ai_cm: {str(e)}") 