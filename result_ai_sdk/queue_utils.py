"""
Queue management for the TestAI SDK.

This module provides queue functionality for batching and processing API requests.
"""

import logging
import queue as std_queue
import threading
import time
from typing import Any, Dict

import requests

# Configure logging
logger = logging.getLogger("result_ai_sdk.queue")
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Create a queue for batching requests
request_queue = std_queue.Queue()
BATCH_SIZE = 1
CHECK_INTERVAL = 0.01
API_ENDPOINT = "https://41aqa6x62g.execute-api.us-east-1.amazonaws.com/prompts"


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
                        requests.post(API_ENDPOINT, json={"prompts": batch}, timeout=5)
                        logger.debug("Batch sent successfully")
                        last_send_time = current_time
                    except Exception as e:
                        logger.error(f"Error sending batch: {e}")
                    batch = []
            except std_queue.Empty:
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
