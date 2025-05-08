"""
Core functionality for the TestAI SDK.

This module provides the main classes and functions for monitoring and
recording OpenAI API calls in Python applications.
"""

from datetime import datetime
import openai
import queue
import time
import requests
import threading
from typing import Any, Dict, List, Optional
import logging

# Configure logging
logger = logging.getLogger("testai_sdk")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Create a queue for batching requests
request_queue = queue.Queue()
BATCH_SIZE = 1
CHECK_INTERVAL = 0.01
API_ENDPOINT = "https://41aqa6x62g.execute-api.us-east-1.amazonaws.com/prompts"

# Worker thread to process the queue
def queue_worker():
    """
    Background worker thread that processes the queue of API requests.
    
    This function runs in a separate thread and periodically checks the queue
    for new items. When items are found, they are batched and sent to the API.
    """
    logger.info("Queue worker started")
    batch = []
    last_send_time = time.time()
    while True:
        # Process all available items in the queue
        while not request_queue.empty():
            try:
                item = request_queue.get_nowait()
                logger.debug(f"Processing item: {item}")
                batch.append(item)
                request_queue.task_done()
                
                current_time = time.time()
                # If batch size reached or timeout exceeded, send immediately
                if len(batch) >= BATCH_SIZE or (current_time - last_send_time) >= 3:
                    try:
                        logger.debug(f"Sending batch of {len(batch)} items")
                        requests.post(
                            API_ENDPOINT,
                            json={"prompts": batch},
                            timeout=5
                        )
                        logger.debug("Batch sent successfully")
                        last_send_time = current_time
                    except Exception as e:
                        logger.error(f"Error sending batch: {e}")
                    batch = []
            except queue.Empty:
                break
        
        # Sleep for the check interval
        time.sleep(CHECK_INTERVAL)

# Start the worker thread
worker_thread = threading.Thread(target=queue_worker)
worker_thread.daemon = True
worker_thread.start()

def add_to_queue(data: Dict[str, Any]) -> None:
    """
    Add data to the request queue for processing.
    
    Args:
        data: The data to add to the queue
    """
    logger.debug(f"Adding to queue: {data}")
    request_queue.put(data)
    logger.debug(f"Added item to queue. Queue size: {request_queue.qsize()}")


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
                    logger.info(f"Creating OpenAI chat completion for task: {self.task_name}")
                    start_time = time.perf_counter()
                    
                    result = self.old_func(*args, **kwargs)
                    
                    time_took = time.perf_counter() - start_time
                    logger.info(f"OpenAI API call completed in {time_took:.3f}s for task: {self.task_name}")

                    request_data = {
                        "type": "openai_request",
                        "timestamp": datetime.now().isoformat(),
                        "input_args": self.input_args,
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

                    logger.info(f"Adding result to queue for task: {self.task_name}")
                    
                    add_to_queue({
                        "user_id": "1897ce6d-5694-41ce-a75d-8ea9e4dc81b4",
                        "task": self.task_name,
                        "request_data": request_data, 
                        "response_data": response_data
                    })    
                    return result
                except Exception as e:
                    logger.error(f"Error in OpenAI API call for task {self.task_name}: {str(e)}")
                    raise
                    
            openai.resources.chat.completions.Completions.create = new_create
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
