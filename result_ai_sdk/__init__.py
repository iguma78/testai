"""
TestAI SDK - A Python SDK for monitoring OpenAI API calls.

This package provides utilities for monitoring and recording OpenAI API calls
in Python applications.
"""

from .patch import result_ai
from .queue_utils import API_SETTINGS

__version__ = "0.1.1"
__all__ = ["result_ai", "API_SETTINGS"]
