"""
Custom exception classes for the Claude Code Hooks Library.

This module defines the exception hierarchy used throughout the library.
All exceptions include descriptive error messages to help developers debug issues.
"""


class CCHooksError(Exception):
    """
    Base exception for all cchooks errors.

    This is the parent class for all library-specific exceptions.
    Catch this exception to handle any error from the hooks library.
    """

    def __init__(self, message: str = None, suggestion: str = None):
        """
        Initialize the exception with a descriptive message.

        Args:
            message: The error message describing what went wrong
            suggestion: Optional suggestion for how to fix the issue
        """
        if message is None:
            message = "An error occurred in the hooks library"

        if suggestion:
            full_message = f"{message}\n\nSuggestion: {suggestion}"
        else:
            full_message = message
        super().__init__(full_message)
        self.message = message
        self.suggestion = suggestion


class UnsupportedHookEventError(CCHooksError):
    """
    Raised when an unsupported hook event name is provided.

    This error occurs when the hook_event_name parameter contains an event
    that is not supported by the Claude hook specification.
    """

    def __init__(self, message: str, supported_events: list = None):
        """
        Initialize with details about supported events.

        Args:
            message: The error message
            supported_events: List of supported event names
        """
        if supported_events:
            suggestion = f"Use one of the supported events: {', '.join(sorted(supported_events))}"
            super().__init__(message, suggestion)
        else:
            super().__init__(message)
        self.supported_events = supported_events


class InvalidDataError(CCHooksError):
    """
    Raised when stdin data is malformed or invalid.

    This error occurs when the stdin parameter contains data that cannot be
    parsed or does not conform to the expected Claude hook data structure.
    """

    def __init__(
        self, message: str, data_type: str = None, expected_format: str = None
    ):
        """
        Initialize with details about the data issue.

        Args:
            message: The error message
            data_type: The type of data that was provided
            expected_format: Description of the expected data format
        """
        if data_type or expected_format:
            suggestion_parts = []
            if expected_format:
                suggestion_parts.append(f"Expected format: {expected_format}")
            if data_type:
                suggestion_parts.append(f"Received: {data_type}")
            suggestion_parts.append(
                "Ensure stdin contains valid JSON with required fields like 'hook_event_name'"
            )
            suggestion = ". ".join(suggestion_parts)
            super().__init__(message, suggestion)
        else:
            super().__init__(message)

        self.data_type = data_type
        self.expected_format = expected_format


class CallbackError(CCHooksError):
    """
    Raised when callback execution fails.

    This error occurs when the provided callback function cannot be executed
    or raises an exception during execution.
    """

    def __init__(
        self, message: str, callback_type: str = None, original_error: str = None
    ):
        """
        Initialize with details about the callback issue.

        Args:
            message: The error message
            callback_type: The type of the callback that failed
            original_error: The original error message if callback raised an exception
        """
        if callback_type or original_error:
            suggestion_parts = ["Ensure your callback function:"]
            suggestion_parts.append(
                "- Is callable (function, method, or callable object)"
            )
            suggestion_parts.append(
                "- Accepts a dictionary parameter containing hook data"
            )
            suggestion_parts.append("- Handles all expected data fields properly")
            if original_error:
                suggestion_parts.append(
                    f"- Addresses the original error: {original_error}"
                )
            suggestion = "\n".join(suggestion_parts)
            super().__init__(message, suggestion)
        else:
            super().__init__(message)

        self.callback_type = callback_type
        self.original_error = original_error


class HookEventMismatchError(CCHooksError):
    """
    Raised when stdin event doesn't match requested hook_event_name.

    This error occurs when the hook_event_name parameter doesn't match
    the event name found in the stdin data.
    """

    def __init__(
        self, message: str, requested_event: str = None, stdin_event: str = None
    ):
        """
        Initialize with details about the mismatch.

        Args:
            message: The error message
            requested_event: The event name that was requested
            stdin_event: The event name found in stdin
        """
        if requested_event and stdin_event:
            suggestion_parts = []
            suggestion_parts.append(
                f"Change hook_event_name from '{requested_event}' to '{stdin_event}'"
            )
            suggestion_parts.append(
                f"Or ensure stdin contains event '{requested_event}' instead of '{stdin_event}'"
            )
            suggestion_parts.append(
                "The hook_event_name parameter must match the 'hook_event_name' field in stdin data"
            )
            suggestion = ". ".join(suggestion_parts)
            super().__init__(message, suggestion)
        else:
            super().__init__(message)

        self.requested_event = requested_event
        self.stdin_event = stdin_event
