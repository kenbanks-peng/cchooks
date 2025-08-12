"""
Core hook processing logic for the Claude Code Hooks Library.

This module contains the main hook function and core processing components.
"""

import logging
from typing import Any, Callable, Dict, Union
from io import TextIOBase
from .exceptions import CallbackError, HookEventMismatchError
from .validators import EventValidator, DataProcessor

# Configure logging for the hooks library
logger = logging.getLogger(__name__)

# Set up a default handler if none exists
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)  # Default to WARNING level


class CallbackManager:
    """
    Manages callback execution with error handling.

    This class provides static methods for validating and executing user-provided
    callback functions in a safe manner with comprehensive error handling.

    The CallbackManager ensures that:
    - Callbacks are callable before execution
    - Callback execution errors are properly caught and wrapped
    - Detailed logging is provided for debugging

    Example:
        >>> def my_callback(data):
        ...     return f"Processed {data['hook_event_name']}"
        >>>
        >>> CallbackManager.validate_callback(my_callback)  # No exception
        >>> result = CallbackManager.execute_callback(my_callback, {"hook_event_name": "Stop"})
        >>> print(result)  # "Processed Stop"
    """

    @staticmethod
    def validate_callback(callback: Any) -> None:
        """
        Validate that the callback is callable.

        Args:
            callback: The callback to validate

        Raises:
            CallbackError: If callback is not callable
        """
        logger.debug(f"Validating callback of type: {type(callback).__name__}")

        if callback is None:
            error_msg = "Callback must be callable, got NoneType"
            logger.error("Callback cannot be None - a callable function is required")
            raise CallbackError(error_msg)

        if not callable(callback):
            error_msg = f"Callback must be callable, got {type(callback).__name__}"
            logger.error(
                f"Callback must be callable (function, method, or callable object), got {type(callback).__name__}"
            )
            raise CallbackError(error_msg)

        logger.debug("Callback validation successful")

    @staticmethod
    def execute_callback(callback: Callable, data: Dict[str, Any]) -> Any:
        """
        Execute the user's callback with proper error handling.

        Args:
            callback: The user-provided callback function
            data: Processed hook event data

        Returns:
            The callback's return value

        Raises:
            CallbackError: If callback execution fails
        """
        logger.debug(f"Executing callback with data keys: {list(data.keys())}")

        try:
            result = callback(data)
            logger.debug(
                f"Callback executed successfully, returned: {type(result).__name__}"
            )
            return result
        except Exception as e:
            error_msg = f"Callback execution failed: {str(e)}"
            logger.error(f"Callback execution failed with {type(e).__name__}: {str(e)}")
            raise CallbackError(error_msg) from e


def hook(
    hook_event_name: str,
    stdin: Union[Dict[str, Any], TextIOBase],
    callback: Callable[[Dict[str, Any]], Any],
) -> Any:
    """
    Process a Claude hook event with the provided callback.

    This is the main entry point for the cchooks library. It handles the complete
    hook processing pipeline: validates the event name, processes input data,
    matches events, and executes the user's callback function.

    The function abstracts away the complexity of the Claude hook specification,
    allowing developers to focus on their hook logic rather than protocol details.

    Args:
        hook_event_name (str): The Claude hook event name to process. Must be one of:
            - 'PreToolUse': Before a tool is executed
            - 'PostToolUse': After a tool is executed
            - 'Notification': For notification events
            - 'Stop': When a session stops
            - 'SubagentStop': When a subagent stops
            - 'UserPromptSubmit': When user submits a prompt
            - 'PreCompact': Before conversation compacting
            - 'SessionStart': When a session starts

        stdin (Union[Dict[str, Any], TextIOBase]): The hook event data, which can be:
            - A dictionary containing hook event data directly
            - A TextIO stream (like sys.stdin) containing JSON-formatted hook data
            The data must contain at least a 'hook_event_name' field that matches
            the hook_event_name parameter.

        callback (Callable[[Dict[str, Any]], Any]): A callable that will be executed
            when the hook event is processed. The callback receives the processed
            hook data as a dictionary parameter and can return any value. The callback
            must be callable (function, method, lambda, or callable object).

    Returns:
        Any: The return value from the callback function. The type depends on what
        your callback returns.

    Raises:
        UnsupportedHookEventError: If hook_event_name is not in the list of supported
            Claude hook events. The exception includes a list of supported events.

        InvalidDataError: If stdin data is malformed, missing required fields, or
            cannot be processed. This includes JSON parsing errors, missing
            'hook_event_name' field, or wrong data types.

        CallbackError: If the callback cannot be executed. This includes cases where
            the callback is not callable, or when the callback raises an exception
            during execution. The original exception is wrapped and preserved.

        HookEventMismatchError: If the 'hook_event_name' field in the stdin data
            doesn't match the hook_event_name parameter. Both must be identical
            for the hook to be processed.

    Example:
        Basic usage with dictionary input:

        >>> from cchooks import hook
        >>>
        >>> def my_callback(data):
        ...     event = data.get("hook_event_name")
        ...     return f"Processed {event} event"
        >>>
        >>> hook_data = {
        ...     "hook_event_name": "Stop",
        ...     "session_id": "session_123",
        ...     "stop_hook_active": False
        ... }
        >>>
        >>> result = hook("Stop", hook_data, my_callback)
        >>> print(result)  # "Processed Stop event"

        Usage with JSON stream input:

        >>> import json
        >>> import io
        >>>
        >>> def tool_callback(data):
        ...     tool_name = data.get("tool_name", "unknown")
        ...     return {"permission": "granted", "tool": tool_name}
        >>>
        >>> json_data = json.dumps({
        ...     "hook_event_name": "PreToolUse",
        ...     "tool_name": "Read",
        ...     "tool_input": {"file_path": "example.txt"}
        ... })
        >>> stream = io.StringIO(json_data)
        >>>
        >>> result = hook("PreToolUse", stream, tool_callback)
        >>> print(result["permission"])  # "granted"

        Error handling:

        >>> from cchooks.exceptions import UnsupportedHookEventError
        >>>
        >>> try:
        ...     hook("InvalidEvent", hook_data, my_callback)
        ... except UnsupportedHookEventError as e:
        ...     print(f"Error: {e}")
        ...     print(f"Supported: {e.supported_events}")

    Note:
        This function is thread-safe and can be called concurrently from multiple
        threads. Each call is independent and maintains no shared state.

        The function performs validation in this order:
        1. Validates hook_event_name against supported events
        2. Validates that callback is callable
        3. Processes and validates stdin data
        4. Checks that stdin event matches requested event
        5. Executes callback with processed data

        All validation errors include helpful suggestions for fixing the issue.
    """
    logger.info(f"Processing hook event: {hook_event_name}")
    logger.debug(
        f"Hook parameters - event: {hook_event_name}, stdin type: {type(stdin).__name__}"
    )

    try:
        # Step 1: Validate the requested hook event name
        logger.debug("Step 1: Validating hook event name")
        EventValidator.validate_event_name(hook_event_name)
        logger.debug(f"Hook event name '{hook_event_name}' is valid")

        # Step 2: Validate the callback
        logger.debug("Step 2: Validating callback")
        CallbackManager.validate_callback(callback)

        # Step 3: Process and validate stdin data
        logger.debug("Step 3: Processing stdin data")
        data = DataProcessor.process_stdin(stdin)
        logger.debug(
            f"Stdin data processed successfully, contains keys: {list(data.keys())}"
        )

        # Step 4: Check if the event in stdin matches the requested event
        logger.debug("Step 4: Checking event name match")
        stdin_event_name = data["hook_event_name"]
        if stdin_event_name != hook_event_name:
            error_msg = f"Hook event mismatch: requested '{hook_event_name}' but stdin contains '{stdin_event_name}'"
            logger.error(error_msg)
            raise HookEventMismatchError(error_msg)

        logger.debug(f"Event names match: {hook_event_name}")

        # Step 5: Execute the callback with the processed data
        logger.debug("Step 5: Executing callback")
        result = CallbackManager.execute_callback(callback, data)

        logger.info(
            f"Hook processing completed successfully for event: {hook_event_name}"
        )
        return result

    except Exception as e:
        logger.error(
            f"Hook processing failed for event '{hook_event_name}': {type(e).__name__}: {str(e)}"
        )
        raise
