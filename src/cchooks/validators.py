"""
Event and data validation components for the Claude Code Hooks Library.

This module contains classes for validating hook event names and processing stdin data.
"""

import json
from typing import Any, Dict, Set, Union
from io import TextIOBase

from .constants import SUPPORTED_HOOK_EVENTS
from .exceptions import UnsupportedHookEventError, InvalidDataError


class EventValidator:
    """
    Validates hook event names against supported Claude events.

    This class provides validation functionality to ensure that hook event names
    are supported by the Claude hook specification. It maintains a list of valid
    event names and provides methods to validate against them.

    Supported events include:
    - PreToolUse: Before a tool is executed
    - PostToolUse: After a tool is executed
    - Notification: For notification events
    - Stop: When a session stops
    - SubagentStop: When a subagent stops
    - UserPromptSubmit: When user submits a prompt
    - PreCompact: Before conversation compacting
    - SessionStart: When a session starts

    Example:
        >>> EventValidator.validate_event_name("Stop")  # No exception
        >>> EventValidator.validate_event_name("InvalidEvent")  # Raises UnsupportedHookEventError
        >>> supported = EventValidator.get_supported_events()
        >>> print("Stop" in supported)  # True
    """

    @classmethod
    def validate_event_name(cls, event_name: str) -> None:
        """
        Validate that the event name is supported.

        Args:
            event_name: The hook event name to validate

        Raises:
            UnsupportedHookEventError: If the event name is not supported
        """
        if not isinstance(event_name, str):
            raise UnsupportedHookEventError(
                f"Hook event name must be a string, got {type(event_name).__name__}",
                supported_events=list(SUPPORTED_HOOK_EVENTS),
            )

        if event_name not in SUPPORTED_HOOK_EVENTS:
            raise UnsupportedHookEventError(
                f"Unsupported hook event '{event_name}'",
                supported_events=list(SUPPORTED_HOOK_EVENTS),
            )

    @classmethod
    def get_supported_events(cls) -> Set[str]:
        """
        Return set of all supported event names.

        Returns:
            Set of supported hook event names
        """
        return SUPPORTED_HOOK_EVENTS.copy()


class DataProcessor:
    """
    Handles parsing and validation of stdin data.

    This class processes input data from various sources (dictionaries or TextIO streams)
    and validates it according to the Claude hook specification. It ensures that all
    required fields are present and properly formatted.

    The DataProcessor can handle:
    - Dictionary input containing hook data
    - TextIO streams with JSON-formatted hook data
    - Validation of required fields like 'hook_event_name'
    - Type checking and format validation

    Example:
        >>> import io
        >>> import json
        >>>
        >>> # Process dictionary input
        >>> data = {"hook_event_name": "Stop", "session_id": "123"}
        >>> result = DataProcessor.process_stdin(data)
        >>> print(result["hook_event_name"])  # "Stop"
        >>>
        >>> # Process JSON stream input
        >>> json_data = json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Read"})
        >>> stream = io.StringIO(json_data)
        >>> result = DataProcessor.process_stdin(stream)
        >>> print(result["tool_name"])  # "Read"
    """

    @staticmethod
    def process_stdin(stdin: Union[Dict[str, Any], TextIOBase]) -> Dict[str, Any]:
        """
        Process stdin data into a validated dictionary.

        Args:
            stdin: Either a dict or TextIO containing JSON data

        Returns:
            Validated dictionary containing hook event data

        Raises:
            InvalidDataError: If data is malformed or missing required fields
        """
        if stdin is None:
            raise InvalidDataError(
                "stdin cannot be None",
                data_type="None",
                expected_format="dictionary or TextIO object with JSON data",
            )

        # Handle dictionary input
        if isinstance(stdin, dict):
            data = stdin
        # Handle TextIO input - check if it has a read method
        elif hasattr(stdin, "read") and callable(getattr(stdin, "read")):
            try:
                content = stdin.read()
                if not content.strip():
                    raise InvalidDataError(
                        "stdin contains no data",
                        data_type="empty TextIO",
                        expected_format="TextIO with JSON content",
                    )
                data = json.loads(content)
            except json.JSONDecodeError as e:
                raise InvalidDataError(
                    f"Invalid JSON in stdin: {e}",
                    data_type="malformed JSON",
                    expected_format="valid JSON object",
                )
            except Exception as e:
                raise InvalidDataError(
                    f"Error reading stdin: {e}",
                    data_type="unreadable TextIO",
                    expected_format="readable TextIO object",
                )
        else:
            raise InvalidDataError(
                f"stdin must be a dictionary or TextIO object, got {type(stdin).__name__}",
                data_type=type(stdin).__name__,
                expected_format="dictionary or TextIO object",
            )

        # Validate the processed data
        DataProcessor.validate_hook_data(data)
        return data

    @staticmethod
    def validate_hook_data(data: Dict[str, Any]) -> None:
        """
        Validate that hook data contains required fields.

        Args:
            data: Dictionary containing hook event data

        Raises:
            InvalidDataError: If data is missing required fields or has invalid structure
        """
        if not isinstance(data, dict):
            raise InvalidDataError(
                f"Hook data must be a dictionary, got {type(data).__name__}",
                data_type=type(data).__name__,
                expected_format="dictionary with 'hook_event_name' field",
            )

        # Check for required field: hook_event_name
        if "hook_event_name" not in data:
            available_fields = list(data.keys()) if data else []
            raise InvalidDataError(
                f"Hook data missing required field 'hook_event_name'. Available fields: {available_fields}",
                data_type="dictionary without required field",
                expected_format="dictionary with 'hook_event_name' field",
            )

        hook_event_name = data["hook_event_name"]
        if not isinstance(hook_event_name, str):
            raise InvalidDataError(
                f"Field 'hook_event_name' must be a string, got {type(hook_event_name).__name__}",
                data_type=f"hook_event_name: {type(hook_event_name).__name__}",
                expected_format="hook_event_name: string",
            )

        if not hook_event_name.strip():
            raise InvalidDataError(
                "Field 'hook_event_name' cannot be empty",
                data_type="empty string",
                expected_format="non-empty string with valid hook event name",
            )
