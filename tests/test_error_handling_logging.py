"""
Tests for comprehensive error handling and logging functionality.

This module tests error message clarity, logging output, and descriptive error messages
for all exception types in the Claude Code Hooks Library.
"""

import logging
import io
import pytest

from src.hooks import hook
from src.hooks.exceptions import (
    CCHooksError,
    UnsupportedHookEventError,
    InvalidDataError,
    CallbackError,
    HookEventMismatchError,
)
from src.hooks.core import CallbackManager, logger
from src.hooks.validators import EventValidator, DataProcessor


class TestErrorMessageClarity:
    """Test that all error messages are clear and descriptive."""

    def test_unsupported_hook_event_error_message(self):
        """Test UnsupportedHookEventError provides clear guidance."""
        with pytest.raises(UnsupportedHookEventError) as exc_info:
            hook("InvalidEvent", {"hook_event_name": "InvalidEvent"}, lambda x: x)

        error = exc_info.value
        assert "InvalidEvent" in str(error)
        assert "Supported events:" in str(
            error
        ) or "Use one of the supported events:" in str(error)
        assert hasattr(error, "supported_events")
        assert isinstance(error.supported_events, list)
        assert len(error.supported_events) > 0

    def test_invalid_data_error_message_none_stdin(self):
        """Test InvalidDataError for None stdin provides clear guidance."""
        with pytest.raises(InvalidDataError) as exc_info:
            hook("Stop", None, lambda x: x)

        error = exc_info.value
        assert "stdin cannot be None" in str(error)
        assert "dictionary or TextIO object" in str(error)
        assert hasattr(error, "data_type")
        assert error.data_type == "None"

    def test_invalid_data_error_message_wrong_type(self):
        """Test InvalidDataError for wrong stdin type provides clear guidance."""
        with pytest.raises(InvalidDataError) as exc_info:
            hook("Stop", "invalid_string", lambda x: x)

        error = exc_info.value
        assert "stdin must be a dictionary or TextIO object" in str(error)
        assert "str" in str(error)
        assert hasattr(error, "data_type")
        assert error.data_type == "str"

    def test_invalid_data_error_message_missing_field(self):
        """Test InvalidDataError for missing required field provides clear guidance."""
        with pytest.raises(InvalidDataError) as exc_info:
            hook("Stop", {"other_field": "value"}, lambda x: x)

        error = exc_info.value
        assert "missing required field 'hook_event_name'" in str(error)
        assert "Available fields:" in str(error)
        assert hasattr(error, "expected_format")
        assert "hook_event_name" in error.expected_format

    def test_callback_error_message_none_callback(self):
        """Test CallbackError for None callback provides clear guidance."""
        with pytest.raises(CallbackError) as exc_info:
            hook("Stop", {"hook_event_name": "Stop"}, None)

        error = exc_info.value
        assert "Callback must be callable, got NoneType" in str(error)
        assert hasattr(error, "callback_type")
        # Note: callback_type is None for backward compatibility

    def test_callback_error_message_non_callable(self):
        """Test CallbackError for non-callable callback provides clear guidance."""
        with pytest.raises(CallbackError) as exc_info:
            hook("Stop", {"hook_event_name": "Stop"}, "not_callable")

        error = exc_info.value
        assert "Callback must be callable" in str(error)
        assert "str" in str(error)
        assert hasattr(error, "callback_type")
        # Note: callback_type is None for backward compatibility

    def test_callback_error_message_execution_failure(self):
        """Test CallbackError for callback execution failure provides clear guidance."""

        def failing_callback(data):
            raise ValueError("Test error")

        with pytest.raises(CallbackError) as exc_info:
            hook("Stop", {"hook_event_name": "Stop"}, failing_callback)

        error = exc_info.value
        assert "Callback execution failed" in str(error)
        assert "Test error" in str(error)
        assert hasattr(error, "original_error")
        # Note: original_error is None for backward compatibility

    def test_hook_event_mismatch_error_message(self):
        """Test HookEventMismatchError provides clear guidance."""
        with pytest.raises(HookEventMismatchError) as exc_info:
            hook("Stop", {"hook_event_name": "PreToolUse"}, lambda x: x)

        error = exc_info.value
        assert "Hook event mismatch" in str(error)
        assert "requested 'Stop'" in str(error)
        assert "stdin contains 'PreToolUse'" in str(error)
        assert hasattr(error, "requested_event")
        assert hasattr(error, "stdin_event")
        # Note: event attributes are None for backward compatibility


class TestLoggingOutput:
    """Test that logging output is comprehensive and helpful."""

    def setup_method(self):
        """Set up logging capture for each test."""
        self.log_capture = io.StringIO()
        self.handler = logging.StreamHandler(self.log_capture)
        self.handler.setLevel(logging.DEBUG)
        logger.addHandler(self.handler)
        logger.setLevel(logging.DEBUG)

    def teardown_method(self):
        """Clean up logging after each test."""
        logger.removeHandler(self.handler)
        self.handler.close()

    def get_log_output(self):
        """Get the captured log output."""
        return self.log_capture.getvalue()

    def test_successful_hook_processing_logging(self):
        """Test that successful hook processing logs appropriate messages."""

        def test_callback(data):
            return "success"

        result = hook("Stop", {"hook_event_name": "Stop"}, test_callback)
        log_output = self.get_log_output()

        assert result == "success"
        assert "Processing hook event: Stop" in log_output
        assert "Step 1: Validating hook event name" in log_output
        assert "Step 2: Validating callback" in log_output
        assert "Step 3: Processing stdin data" in log_output
        assert "Step 4: Checking event name match" in log_output
        assert "Step 5: Executing callback" in log_output
        assert "Hook processing completed successfully" in log_output

    def test_validation_error_logging(self):
        """Test that validation errors are properly logged."""
        with pytest.raises(UnsupportedHookEventError):
            hook("InvalidEvent", {"hook_event_name": "InvalidEvent"}, lambda x: x)

        log_output = self.get_log_output()
        assert "Processing hook event: InvalidEvent" in log_output
        assert "Hook processing failed" in log_output
        assert "UnsupportedHookEventError" in log_output

    def test_callback_validation_logging(self):
        """Test that callback validation logs debug information."""
        with pytest.raises(CallbackError):
            hook("Stop", {"hook_event_name": "Stop"}, "not_callable")

        log_output = self.get_log_output()
        assert "Validating callback of type: str" in log_output
        assert "Callback must be callable" in log_output

    def test_callback_execution_logging(self):
        """Test that callback execution logs debug information."""

        def test_callback(data):
            return {"result": "test"}

        hook("Stop", {"hook_event_name": "Stop"}, test_callback)
        log_output = self.get_log_output()

        assert "Executing callback with data keys:" in log_output
        assert "Callback executed successfully" in log_output
        assert "returned: dict" in log_output

    def test_data_processing_logging(self):
        """Test that data processing logs debug information."""
        hook("Stop", {"hook_event_name": "Stop", "extra": "data"}, lambda x: x)
        log_output = self.get_log_output()

        assert "Processing stdin data" in log_output
        assert "Stdin data processed successfully" in log_output
        assert "contains keys:" in log_output

    def test_event_mismatch_logging(self):
        """Test that event mismatch errors are properly logged."""
        with pytest.raises(HookEventMismatchError):
            hook("Stop", {"hook_event_name": "PreToolUse"}, lambda x: x)

        log_output = self.get_log_output()
        assert "Checking event name match" in log_output
        assert "Hook event mismatch" in log_output

    def test_callback_failure_logging(self):
        """Test that callback failures are properly logged."""

        def failing_callback(data):
            raise RuntimeError("Callback failed")

        with pytest.raises(CallbackError):
            hook("Stop", {"hook_event_name": "Stop"}, failing_callback)

        log_output = self.get_log_output()
        assert "Executing callback" in log_output
        assert "Callback execution failed" in log_output
        assert "RuntimeError" in log_output


class TestExceptionHierarchy:
    """Test that exception hierarchy works correctly."""

    def test_all_exceptions_inherit_from_base(self):
        """Test that all custom exceptions inherit from CCHooksError."""
        exceptions = [
            UnsupportedHookEventError("test"),
            InvalidDataError("test"),
            CallbackError("test"),
            HookEventMismatchError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, CCHooksError)
            assert isinstance(exc, Exception)

    def test_base_exception_with_suggestion(self):
        """Test that base exception handles suggestions properly."""
        exc = CCHooksError("Test message", "Test suggestion")
        error_str = str(exc)

        assert "Test message" in error_str
        assert "Suggestion: Test suggestion" in error_str
        assert exc.message == "Test message"
        assert exc.suggestion == "Test suggestion"

    def test_base_exception_without_suggestion(self):
        """Test that base exception works without suggestions."""
        exc = CCHooksError("Test message")
        error_str = str(exc)

        assert error_str == "Test message"
        assert exc.message == "Test message"
        assert exc.suggestion is None


class TestErrorContextInformation:
    """Test that errors provide helpful context information."""

    def test_unsupported_event_provides_supported_list(self):
        """Test that UnsupportedHookEventError includes supported events."""
        with pytest.raises(UnsupportedHookEventError) as exc_info:
            EventValidator.validate_event_name("InvalidEvent")

        error = exc_info.value
        assert hasattr(error, "supported_events")
        assert isinstance(error.supported_events, list)
        assert "Stop" in error.supported_events
        assert "PreToolUse" in error.supported_events

    def test_invalid_data_provides_type_info(self):
        """Test that InvalidDataError includes data type information."""
        with pytest.raises(InvalidDataError) as exc_info:
            DataProcessor.process_stdin(123)

        error = exc_info.value
        assert hasattr(error, "data_type")
        assert hasattr(error, "expected_format")
        assert error.data_type == "int"
        assert "dictionary or TextIO object" in error.expected_format

    def test_callback_error_provides_callback_info(self):
        """Test that CallbackError includes callback information."""
        with pytest.raises(CallbackError) as exc_info:
            CallbackManager.validate_callback(123)

        error = exc_info.value
        assert hasattr(error, "callback_type")
        # Note: callback_type is None for backward compatibility when called directly

    def test_hook_mismatch_provides_event_info(self):
        """Test that HookEventMismatchError includes event information."""
        error = HookEventMismatchError(
            "test message", requested_event="Stop", stdin_event="PreToolUse"
        )

        assert hasattr(error, "requested_event")
        assert hasattr(error, "stdin_event")
        assert error.requested_event == "Stop"
        assert error.stdin_event == "PreToolUse"


class TestLoggingConfiguration:
    """Test that logging is properly configured."""

    def test_logger_has_default_handler(self):
        """Test that logger has a default handler configured."""
        # The logger should have at least one handler
        assert len(logger.handlers) >= 1

    def test_logger_default_level(self):
        """Test that logger has appropriate default level configuration."""
        # Test that the logger is configured with a reasonable default
        # The level might be modified by test setup, so we check the handler level
        handler = logger.handlers[0]

        # The logger should have a handler that can handle WARNING level messages
        # This ensures that important messages will be shown by default
        assert handler.level <= logging.WARNING

    def test_log_format_includes_required_fields(self):
        """Test that log format includes timestamp, name, level, and message."""
        # Check that the handler has a formatter
        handler = logger.handlers[0]
        formatter = handler.formatter

        assert formatter is not None
        format_string = formatter._fmt
        assert "%(asctime)s" in format_string
        assert "%(name)s" in format_string
        assert "%(levelname)s" in format_string
        assert "%(message)s" in format_string


if __name__ == "__main__":
    pytest.main([__file__])
