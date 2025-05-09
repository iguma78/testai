import copy
import datetime
import importlib
import inspect
import logging
import time
import traceback
from pydantic import BaseModel
import wrapt
from typing import Any, Callable, Optional
from packaging import version

from result_ai_sdk.queue_utils import add_to_queue

logger = logging.getLogger("result_ai_sdk")

def _patch_func(module_name_to_patch: str, func_name_to_patch: str, new_func: Callable):
    (parent, attribute, original) = wrapt.resolve_path(module_name_to_patch, func_name_to_patch)
    setattr(parent, attribute, new_func)
    return original

def _wrap_func(module_name_to_patch: str, func_name_to_patch: str, wrapper: Callable):
    (parent, attribute, original) = wrapt.resolve_path(module_name_to_patch, func_name_to_patch)
    setattr(parent, attribute, wrapper(original))
    return original

class FunctionPatcher(BaseModel):
    module_name_to_patch: str
    func_name_to_patch: str
    root_module_name: str
    min_module_version: Optional[str] = None
    max_module_version: Optional[str] = None
    patched: bool = False
    original_func: Optional[Callable] = None

    def is_module_version_supported(self) -> bool:
        try:
            module = importlib.import_module(self.root_module_name)
            
            module_version = version.parse(module.__version__)
            
            if self.min_module_version is not None:
                min_version = version.parse(self.min_module_version)
                if module_version < min_version:
                    logger.debug(f"Result AI | Skipping patch for {self.module_name_to_patch} because it's not supported (version {module_version} is less than {min_version}).")
                    return False
                
            if self.max_module_version is not None:
                max_version = version.parse(self.max_module_version)
                if module_version > max_version:
                    logger.debug(f"Result AI | Skipping patch for {self.module_name_to_patch} because it's not supported (version {module_version} is greater than {max_version}).")
                    return False
            return True
        except ImportError:
            logger.debug(f"Result AI | Skipping patch for {self.module_name_to_patch} because it's not installed.")
            return False

    def patch(self, wrapper: Callable):
        if not self.is_module_version_supported():
            return
        
        self.original_func = _wrap_func(self.module_name_to_patch, self.func_name_to_patch, wrapper)
        self.patched = True

    def unpatch(self):
        if not self.patched:
            return
        
        _patch_func(self.module_name_to_patch, self.func_name_to_patch, self.original_func)
        self.original_func = None

SUPPORTED_MODULES_TO_PATCH = [
    FunctionPatcher(
        module_name_to_patch="openai.resources.chat.completions",
        func_name_to_patch="Completions.create",
        root_module_name="openai",
        min_module_version="1.0.0",
        max_module_version=None,
    )
]

class result_ai:
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
        self.task_name = task_name
        self.input_args_to_report = kwargs
        self.patchers = copy.deepcopy(SUPPORTED_MODULES_TO_PATCH)
        
    def __enter__(self):
        for patcher in self.patchers:
            @wrapt.decorator
            def result_ai_wrapper(wrapped, instance, args, kwargs):  
                pre_hook_success = False
                try:
                    logger.debug(f"Result AI | API call started for task: {self.task_name}")
                    start_time = time.perf_counter()
                    pre_hook_success = True
                except Exception:
                    logger.error(f"Result AI | Error in pre hook API call for task {self.task_name}: {traceback.format_exc()}")
                
                response = wrapped(*args, **kwargs)
                
                if pre_hook_success:
                    try:
                        time_took = time.perf_counter() - start_time
                        logger.debug(f"Result AI | API call completed in {time_took:.3f}s for task: {self.task_name}")

                        request_data = {
                            "llm_call_arguments": inspect.signature(wrapped).bind(*args, **kwargs).arguments,
                        }

                        response_data = {
                            "success": True,
                            "response": response,
                            "latency": time_took
                        }

                        logger.debug(f"Result AI | Adding result to queue for task: {self.task_name}")
                        
                        add_to_queue({
                            "user_id": "1897ce6d-5694-41ce-a75d-8ea9e4dc81b4",
                            "function_patched": patcher.func_name_to_patch,
                            "module_name_to_patch": patcher.module_name_to_patch,
                            "root_module_name": patcher.root_module_name,
                            "timestamp": datetime.datetime.now().isoformat(),
                            "task_name": self.task_name,
                            "user_input_args": self.input_args_to_report,
                            "request_data": request_data, 
                            "response_data": response_data
                        })
                                    
                    except Exception:
                        logger.error(f"Result AI | Error in post hook API call for task {self.task_name}: {traceback.format_exc()}")
                
                return response

            patcher.patch(wrapper=result_ai_wrapper)

    def __exit__(self, exctype, excinst, exctb):
        for patcher in self.patchers:
            patcher.unpatch()
