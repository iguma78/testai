"""
Queue management for the TestAI SDK.

This module provides queue functionality for batching and processing API requests.
"""

import os
import time
import queue as std_queue
import logging
import threading
from typing import Any, Dict

import requests

API_SETTINGS = {"endpoint": "https://resultai-862818623075.europe-west1.run.app/prompts"}
# for local run only
# API_SETTINGS = {"endpoint": "http://localhost:8080/prompts"}

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
CHECK_INTERVAL = 0.1


def queue_worker():
    """
    Background worker thread that processes the queue of API requests.

    This function runs in a separate thread and periodically checks the queue
    for new items. When items are found, they are batched and sent to the API.
    """
    logger.debug("Queue worker started")
    batch = []
    last_send_time = time.time()
    notified_no_api_key = False

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
                        api_key = os.getenv("RESULTAI_API_KEY", "")
                        if not api_key and not notified_no_api_key:
                            logger.warning(
                                "RESULTAI_API_KEY environment variable is not set. Monitoring will not be enabled."
                            )
                            notified_no_api_key = True

                        logger.debug(f"Sending batch of {len(batch)} items")
                        response = requests.post(
                            API_SETTINGS["endpoint"], json={"prompts": batch, "api_key": api_key}, timeout=10
                        )
                        logger.debug(f"Batch sent successfully. Response: {response.json()}")
                        last_send_time = current_time
                    except Exception as e:
                        logger.error(f"Error sending batch: {e}")
                    batch = []

            except std_queue.Empty:
                break

        # Sleep for the check interval
        time.sleep(CHECK_INTERVAL)


# Start the worker thread
def start_queue_worker():
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
