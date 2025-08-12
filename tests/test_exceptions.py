#!/usr/bin/env python3
"""
Unit tests for the Claude Code Hooks Library exception classes.

This module tests the custom exception hierarchy defined in src/hooks/exceptions.py.
"""

import pytest
from src.hooks.exceptions import (
    CCHooksError,
    UnsupportedHookEventError,
    InvalidDataError,
    CallbackError,
    HookEventMismatchError,
)


class TestCCHooksError:
    """Test the base CCHooksError exception class."""

    def test_base_exception_creation(self):
        """Test that CCHooksError can be created with a message."""
        message = "Test error message"
        error = CCHooksError(message)

        assert str(error) == message
        assert isinstance(error, Exception)

    def test_base_exception_inheritance(self):
        """Test that CCHooksError inherits from Exception."""
        error = CCHooksError("test")
        assert isinstance(error, Exception)

    def test_base_exception_without_message(self):
        """Test that CCHooksError can be created without a message."""
        error = CCHooksError()
        assert str(error) == "An error occurred in the hooks library"


class TestUnsupportedHookEventError:
    """Test the UnsupportedHookEventError exception class."""

    def test_unsupported_hook_event_error_creation(self):
        """Test that UnsupportedHookEventError can be created with a message."""
        message = "Unsupported hook event 'InvalidEvent'"
        error = UnsupportedHookEventError(message)

        assert str(error) == message
        assert isinstance(error, CCHooksError)
        assert isinstance(error, Exception)

    def test_unsupported_hook_event_error_inheritance(self):
        """Test that UnsupportedHookEventError inherits from CCHooksError."""
        error = UnsupportedHookEventError("test")
        assert isinstance(error, CCHooksError)
        assert isinstance(error, Exception)

    def test_unsupported_hook_event_error_with_event_name(self):
        """Test creating error with specific event name information."""
        event_name = "InvalidEvent"
        supported_events = "PreToolUse, PostToolUse, Stop"
        message = f"Unsupported hook event '{event_name}'. Supported events: {supported_events}"

        error = UnsupportedHookEventError(message)
        assert event_name in str(error)
        assert supported_events in str(error)


class TestInvalidDataError:
    """Test the InvalidDataError exception class."""

    def test_invalid_data_error_creation(self):
        """Test that InvalidDataError can be created with a message."""
        message = "Invalid stdin data: missing required field 'hook_event_name'"
        error = InvalidDataError(message)

        assert str(error) == message
        assert isinstance(error, CCHooksError)
        assert isinstance(error, Exception)

    def test_invalid_data_error_inheritance(self):
        """Test that InvalidDataError inherits from CCHooksError."""
        error = InvalidDataError("test")
        assert isinstance(error, CCHooksError)
        assert isinstance(error, Exception)

    def test_invalid_data_error_with_field_info(self):
        """Test creating error with specific field information."""
        field_name = "hook_event_name"
        message = f"Invalid stdin data: missing required field '{field_name}'"

        error = InvalidDataError(message)
        assert field_name in str(error)
        assert "missing required field" in str(error)


class TestCallbackError:
    """Test the CallbackError exception class."""

    def test_callback_error_creation(self):
        """Test that CallbackError can be created with a message."""
        message = "Callback execution failed: callback must be callable"
        error = CallbackError(message)

        assert str(error) == message
        assert isinstance(error, CCHooksError)
        assert isinstance(error, Exception)

    def test_callback_error_inheritance(self):
        """Test that CallbackError inherits from CCHooksError."""
        error = CallbackError("test")
        assert isinstance(error, CCHooksError)
        assert isinstance(error, Exception)

    def test_callback_error_with_type_info(self):
        """Test creating error with callback type information."""
        callback_type = "<class 'str'>"
        message = (
            f"Callback execution failed: callback must be callable, got {callback_type}"
        )

        error = CallbackError(message)
        assert callback_type in str(error)
        assert "must be callable" in str(error)


class TestHookEventMismatchError:
    """Test the HookEventMismatchError exception class."""

    def test_hook_event_mismatch_error_creation(self):
        """Test that HookEventMismatchError can be created with a message."""
        message = (
            "Hook event mismatch: requested 'Stop' but stdin contains 'PreToolUse'"
        )
        error = HookEventMismatchError(message)

        assert str(error) == message
        assert isinstance(error, CCHooksError)
        assert isinstance(error, Exception)

    def test_hook_event_mismatch_error_inheritance(self):
        """Test that HookEventMismatchError inherits from CCHooksError."""
        error = HookEventMismatchError("test")
        assert isinstance(error, CCHooksError)
        assert isinstance(error, Exception)

    def test_hook_event_mismatch_error_with_event_names(self):
        """Test creating error with specific event name information."""
        requested_event = "Stop"
        stdin_event = "PreToolUse"
        message = f"Hook event mismatch: requested '{requested_event}' but stdin contains '{stdin_event}'"

        error = HookEventMismatchError(message)
        assert requested_event in str(error)
        assert stdin_event in str(error)
        assert "mismatch" in str(error)


class TestExceptionHierarchy:
    """Test the overall exception hierarchy and relationships."""

    def test_all_exceptions_inherit_from_base(self):
        """Test that all custom exceptions inherit from CCHooksError."""
        exceptions = [
            UnsupportedHookEventError("test"),
            InvalidDataError("test"),
            CallbackError("test"),
            HookEventMismatchError("test"),
        ]

        for exception in exceptions:
            assert isinstance(exception, CCHooksError)
            assert isinstance(exception, Exception)

    def test_exception_types_are_distinct(self):
        """Test that different exception types can be distinguished."""
        unsupported_error = UnsupportedHookEventError("test")
        invalid_data_error = InvalidDataError("test")
        callback_error = CallbackError("test")
        mismatch_error = HookEventMismatchError("test")

        # Test that each exception is only an instance of its own type
        assert not isinstance(unsupported_error, InvalidDataError)
        assert not isinstance(unsupported_error, CallbackError)
        assert not isinstance(unsupported_error, HookEventMismatchError)

        assert not isinstance(invalid_data_error, UnsupportedHookEventError)
        assert not isinstance(invalid_data_error, CallbackError)
        assert not isinstance(invalid_data_error, HookEventMismatchError)

        assert not isinstance(callback_error, UnsupportedHookEventError)
        assert not isinstance(callback_error, InvalidDataError)
        assert not isinstance(callback_error, HookEventMismatchError)

        assert not isinstance(mismatch_error, UnsupportedHookEventError)
        assert not isinstance(mismatch_error, InvalidDataError)
        assert not isinstance(mismatch_error, CallbackError)

    def test_exception_catching_hierarchy(self):
        """Test that exceptions can be caught by their base class."""
        exceptions = [
            UnsupportedHookEventError("test"),
            InvalidDataError("test"),
            CallbackError("test"),
            HookEventMismatchError("test"),
        ]

        for exception in exceptions:
            try:
                raise exception
            except CCHooksError as e:
                assert e is exception
            except Exception:
                pytest.fail("Exception should have been caught as CCHooksError")


if __name__ == "__main__":
    pytest.main([__file__])
