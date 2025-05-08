"""
TestAI SDK - A Python SDK for monitoring OpenAI API calls.

This package provides utilities for monitoring and recording OpenAI API calls
in Python applications.
"""

from .core import result_ai_cm, add_to_queue

__version__ = "0.1.0"
__all__ = ["result_ai_cm", "add_to_queue"]
