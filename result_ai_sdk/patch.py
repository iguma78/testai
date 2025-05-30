import os
import copy
import json
import time
import string
import inspect
import logging
import datetime
import traceback
from typing import Callable, Optional
from importlib.metadata import version as importlib_version

import wrapt
import jsonpickle
from pydantic import BaseModel
from packaging import version

from result_ai_sdk.queue_utils import add_to_queue, start_queue_worker

logger = logging.getLogger("result_ai_sdk")

start_queue_worker()


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
            module_version = version.parse(importlib_version(self.root_module_name))

            if self.min_module_version is not None:
                min_version = version.parse(self.min_module_version)
                if module_version < min_version:
                    logger.debug(
                        f"Result AI | Skipping patch for {self.module_name_to_patch} "
                        f"because it's not supported "
                        f"(version {module_version} is less than {min_version})."
                    )
                    return False

            if self.max_module_version is not None:
                max_version = version.parse(self.max_module_version)
                if module_version > max_version:
                    logger.debug(
                        f"Result AI | Skipping patch for {self.module_name_to_patch} "
                        f"because it's not supported "
                        f"(version {module_version} is greater than {max_version})."
                    )
                    return False
            return True
        except ImportError:
            logger.debug(f"Result AI | Skipping patch for {self.module_name_to_patch} because it's not installed.")
            return False

    def patch(self, wrapper: Callable):
        if not self.is_module_version_supported():
            return

        self.original_func = _wrap_func(
            self.module_name_to_patch,
            self.func_name_to_patch,
            wrapper,
        )
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
    ),
    FunctionPatcher(
        module_name_to_patch="langchain_core.language_models",
        func_name_to_patch="BaseChatModel.generate",
        root_module_name="langchain_core",
        min_module_version="0.3.0",
        max_module_version=None,
    ),
]


def convert_to_json_serializable(obj, show_warning: bool):
    try:
        json.dumps(obj)
        return obj
    except TypeError as e:
        new_obj = json.loads(jsonpickle.encode(obj, unpicklable=False, fail_safe=str))
        if show_warning:
            logger.warning(
                f"Result AI | Object {obj} is not JSON serializable, converting to JSON string: {obj} because of {e}"
            )
        return new_obj


def result_ai_wrapper_with_arguments(
    task_name: str, prompt_template: str, args_to_report: dict, metadata: dict, patcher: FunctionPatcher
):
    @wrapt.decorator
    def result_ai_wrapper(wrapped, _instance, args, kwargs):
        pre_hook_success = False
        try:
            logger.debug(f"Result AI | API call started for task: {task_name}")
            start_time = time.perf_counter()
            pre_hook_success = True
        except Exception:
            logger.error(f"Result AI | Error in pre hook API call for task {task_name}: {traceback.format_exc()}")

        response = wrapped(*args, **kwargs)
        if pre_hook_success:
            try:
                time_took = time.perf_counter() - start_time
                logger.debug(f"Result AI | API call completed in {time_took:.3f}s for task: {task_name}")

                instance_dict = {}
                if hasattr(_instance, "__dict__"):
                    instance_dict = {
                        "is_cache": _instance.__dict__.get("cache") is not None,
                        "model": _instance.__dict__.get("model_id"),
                        "max_tokens": _instance.__dict__.get("max_tokens"),
                        "temperature": _instance.__dict__.get("temperature"),
                    }

                arguments = inspect.signature(obj=wrapped).bind(*args, **kwargs).arguments

                request_data = {
                    "llm_call_instance": instance_dict,
                    "llm_call_instance_type": str(type(_instance)),
                    "llm_call_instance_type_name": type(_instance).__name__,
                    "llm_call_arguments": convert_to_json_serializable(arguments, show_warning=False),
                }

                response_data = {
                    "success": True,
                    "usage_metadata": response.generations[0][0].message.usage_metadata,
                    "response": convert_to_json_serializable(
                        response.dict() if hasattr(response, "dict") else response, show_warning=False
                    ),
                    "latency": time_took,
                }

                logger.debug(f"Result AI | Adding result to queue for task: {task_name}")

                add_to_queue(
                    {
                        "function_patched": str(patcher.func_name_to_patch),
                        "module_patched": str(patcher.module_name_to_patch),
                        "root_module_name_patched": str(patcher.root_module_name),
                        "timestamp": datetime.datetime.now().isoformat(),
                        "task_name": task_name,
                        "prompt_template": prompt_template,
                        "user_input_args": convert_to_json_serializable(args_to_report, show_warning=True),
                        "metadata": convert_to_json_serializable(metadata, show_warning=True),
                        "request_data": request_data,
                        "response_data": response_data,
                    }
                )

            except Exception:
                logger.error(f"Result AI | Error in post hook API call for task {task_name}: {traceback.format_exc()}")

        return response

    return result_ai_wrapper


class result_ai:
    def __init__(
        self, task_name: str, prompt_template: str, metadata: Optional[dict] = None, enabled: bool = True, **kwargs
    ):
        self.enabled = enabled and os.getenv("RESULTAI_ENABLED", "true").lower() != "false"
        if not self.enabled:
            return
        self.task_name = task_name
        self.prompt_template = prompt_template
        self.input_args_to_report = kwargs
        try:
            keywords_in_prompt_template = [
                field_name for _, field_name, _, _ in string.Formatter().parse(prompt_template) if field_name
            ]
            if set(keywords_in_prompt_template) != set(kwargs.keys()) and len(keywords_in_prompt_template) == len(
                set(kwargs.keys())
            ):
                logger.warning(
                    f"Result AI | Prompt template {prompt_template} has keywords {keywords_in_prompt_template} "
                    f"that do not match the input arguments {kwargs.keys()}"
                )
        except Exception:
            logger.error(
                f"Result AI | Error in prompt template validation for task {task_name}: {traceback.format_exc()}"
            )

        self.metadata = metadata if metadata is not None else {}

        self.patchers = copy.deepcopy(SUPPORTED_MODULES_TO_PATCH)

    def __enter__(self):
        if not self.enabled:
            return
        for patcher in self.patchers:
            patcher.patch(
                wrapper=result_ai_wrapper_with_arguments(
                    task_name=self.task_name,
                    prompt_template=self.prompt_template,
                    args_to_report=self.input_args_to_report,
                    metadata=self.metadata,
                    patcher=patcher,
                )
            )

    def __exit__(self, exctype, excinst, exctb):
        if not self.enabled:
            return
        for patcher in self.patchers:
            patcher.unpatch()
