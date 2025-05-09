"""
OpenAI plugin for the TestAI SDK.

This module provides OpenAI-specific monitoring functionality.
"""

import time
from datetime import datetime
import logging
from typing import Any, Dict

from ..queue import add_to_queue

logger = logging.getLogger("testai_sdk")

def monitor_openai_call(task_name: str, input_args: Dict[str, Any], original_func: Any):
    """
    Monitor an OpenAI API call and record its metrics.
    
    Args:
        task_name: A string identifier for the current task
        input_args: Additional arguments to be stored with the API call data
        original_func: The original OpenAI API function to call
    
    Returns:
        A wrapped function that monitors the API call
    """
    def new_create(*args, **kwargs):
        """
        Replacement function for the OpenAI API call.
        
        This function wraps the original API call, records metrics about
        the call, and sends the data to the queue for processing.
        
        Args:
            *args: Positional arguments to pass to the original function
            **kwargs: Keyword arguments to pass to the original function
        
        Returns:
            The result of the original function call
        """
        try:
            # Prepare data
            logger.info(f"Creating OpenAI chat completion for task: {task_name}")
            start_time = time.perf_counter()
            
            result = original_func(*args, **kwargs)
            
            time_took = time.perf_counter() - start_time
            logger.info(f"OpenAI API call completed in {time_took:.3f}s for task: {task_name}")

            request_data = {
                "type": "openai_request",
                "timestamp": datetime.now().isoformat(),
                "input_args": input_args,
                "request": {"kwargs": kwargs},
            }

            response_data = {
                "success": True,
                "choices_count": len(result.choices),
                "total_tokens": result.usage.total_tokens,
                "completion_tokens": result.usage.completion_tokens,
                "prompt_tokens": result.usage.prompt_tokens,
                "completion": result.choices[0].message.content,
                "latency": time_took
            }

            logger.info(f"Adding result to queue for task: {task_name}")
            
            add_to_queue({
                "user_id": "1897ce6d-5694-41ce-a75d-8ea9e4dc81b4",
                "task": task_name,
                "request_data": request_data, 
                "response_data": response_data
            })    
            return result
        except Exception as e:
            logger.error(f"Error in OpenAI API call for task {task_name}: {str(e)}")
            raise
            
    return new_create 