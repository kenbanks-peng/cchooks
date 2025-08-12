"""
Unit tests for the core module of the Claude Code Hooks Library.

This module tests the CallbackManager class and the main hook function.
"""

import unittest
from unittest.mock import Mock
from io import StringIO
from src.hooks.core import CallbackManager, hook
from src.hooks.exceptions import (
    CallbackError,
    UnsupportedHookEventError,
    InvalidDataError,
    HookEventMismatchError,
)


class TestCallbackManager(unittest.TestCase):
    """Test cases for the CallbackManager class."""

    def test_validate_callback_with_valid_function(self):
        """Test that validate_callback accepts a valid function."""

        def valid_callback(data):
            return data

        # Should not raise any exception
        CallbackManager.validate_callback(valid_callback)

    def test_validate_callback_with_lambda(self):
        """Test that validate_callback accepts a lambda function."""

        def lambda_callback(data):
            return data

        # Should not raise any exception
        CallbackManager.validate_callback(lambda_callback)

    def test_validate_callback_with_callable_object(self):
        """Test that validate_callback accepts a callable object."""

        class CallableClass:
            def __call__(self, data):
                return data

        callable_obj = CallableClass()

        # Should not raise any exception
        CallbackManager.validate_callback(callable_obj)

    def test_validate_callback_with_mock(self):
        """Test that validate_callback accepts a mock object."""
        mock_callback = Mock()

        # Should not raise any exception
        CallbackManager.validate_callback(mock_callback)

    def test_validate_callback_with_string_raises_error(self):
        """Test that validate_callback raises CallbackError for string."""
        with self.assertRaises(CallbackError) as context:
            CallbackManager.validate_callback("not_callable")

        self.assertIn("Callback must be callable, got str", str(context.exception))

    def test_validate_callback_with_integer_raises_error(self):
        """Test that validate_callback raises CallbackError for integer."""
        with self.assertRaises(CallbackError) as context:
            CallbackManager.validate_callback(42)

        self.assertIn("Callback must be callable, got int", str(context.exception))

    def test_validate_callback_with_none_raises_error(self):
        """Test that validate_callback raises CallbackError for None."""
        with self.assertRaises(CallbackError) as context:
            CallbackManager.validate_callback(None)

        self.assertIn("Callback must be callable, got NoneType", str(context.exception))

    def test_validate_callback_with_list_raises_error(self):
        """Test that validate_callback raises CallbackError for list."""
        with self.assertRaises(CallbackError) as context:
            CallbackManager.validate_callback([1, 2, 3])

        self.assertIn("Callback must be callable, got list", str(context.exception))

    def test_execute_callback_with_successful_function(self):
        """Test that execute_callback successfully executes a function."""

        def test_callback(data):
            return data.get("result", "default")

        test_data = {"result": "success", "other": "value"}
        result = CallbackManager.execute_callback(test_callback, test_data)

        self.assertEqual(result, "success")

    def test_execute_callback_with_lambda(self):
        """Test that execute_callback successfully executes a lambda."""

        def lambda_callback(data):
            return data["count"] * 2

        test_data = {"count": 5}
        result = CallbackManager.execute_callback(lambda_callback, test_data)

        self.assertEqual(result, 10)

    def test_execute_callback_with_callable_object(self):
        """Test that execute_callback successfully executes a callable object."""

        class CallableClass:
            def __call__(self, data):
                return f"Processed: {data.get('message', 'no message')}"

        callable_obj = CallableClass()
        test_data = {"message": "hello world"}
        result = CallbackManager.execute_callback(callable_obj, test_data)

        self.assertEqual(result, "Processed: hello world")

    def test_execute_callback_with_mock(self):
        """Test that execute_callback successfully executes a mock."""
        mock_callback = Mock(return_value="mocked_result")
        test_data = {"key": "value"}

        result = CallbackManager.execute_callback(mock_callback, test_data)

        self.assertEqual(result, "mocked_result")
        mock_callback.assert_called_once_with(test_data)

    def test_execute_callback_with_no_return_value(self):
        """Test that execute_callback handles functions with no return value."""

        def void_callback(data):
            # Function that doesn't return anything
            pass

        test_data = {"key": "value"}
        result = CallbackManager.execute_callback(void_callback, test_data)

        self.assertIsNone(result)

    def test_execute_callback_with_exception_in_callback(self):
        """Test that execute_callback raises CallbackError when callback raises exception."""

        def failing_callback(data):
            raise ValueError("Something went wrong")

        test_data = {"key": "value"}

        with self.assertRaises(CallbackError) as context:
            CallbackManager.execute_callback(failing_callback, test_data)

        self.assertIn(
            "Callback execution failed: Something went wrong", str(context.exception)
        )
        # Check that the original exception is preserved as the cause
        self.assertIsInstance(context.exception.__cause__, ValueError)

    def test_execute_callback_with_key_error_in_callback(self):
        """Test that execute_callback handles KeyError in callback."""

        def key_error_callback(data):
            return data["nonexistent_key"]

        test_data = {"existing_key": "value"}

        with self.assertRaises(CallbackError) as context:
            CallbackManager.execute_callback(key_error_callback, test_data)

        self.assertIn("Callback execution failed:", str(context.exception))
        self.assertIsInstance(context.exception.__cause__, KeyError)

    def test_execute_callback_with_type_error_in_callback(self):
        """Test that execute_callback handles TypeError in callback."""

        def type_error_callback(data):
            return data + "string"  # This will cause TypeError if data is not a string

        test_data = {"key": "value"}  # data is a dict, not a string

        with self.assertRaises(CallbackError) as context:
            CallbackManager.execute_callback(type_error_callback, test_data)

        self.assertIn("Callback execution failed:", str(context.exception))
        self.assertIsInstance(context.exception.__cause__, TypeError)

    def test_execute_callback_preserves_original_exception_chain(self):
        """Test that execute_callback preserves the original exception chain."""

        def nested_exception_callback(data):
            try:
                raise ValueError("Inner error")
            except ValueError as e:
                raise RuntimeError("Outer error") from e

        test_data = {"key": "value"}

        with self.assertRaises(CallbackError) as context:
            CallbackManager.execute_callback(nested_exception_callback, test_data)

        # Check that the CallbackError wraps the RuntimeError
        self.assertIsInstance(context.exception.__cause__, RuntimeError)
        # Check that the original ValueError is still in the chain
        self.assertIsInstance(context.exception.__cause__.__cause__, ValueError)


class TestHookFunction(unittest.TestCase):
    """Test cases for the main hook function."""

    def test_hook_with_valid_dict_input_and_matching_event(self):
        """Test hook function with valid dictionary input and matching event."""

        def test_callback(data):
            return f"Processed: {data['hook_event_name']}"

        test_data = {
            "hook_event_name": "Stop",
            "session_id": "test_session",
            "stop_hook_active": True,
        }

        result = hook("Stop", test_data, test_callback)
        self.assertEqual(result, "Processed: Stop")

    def test_hook_with_valid_textio_input_and_matching_event(self):
        """Test hook function with valid TextIO input and matching event."""

        def test_callback(data):
            return data["tool_name"]

        json_data = '{"hook_event_name": "PreToolUse", "tool_name": "test_tool", "tool_input": {}}'
        stdin_stream = StringIO(json_data)

        result = hook("PreToolUse", stdin_stream, test_callback)
        self.assertEqual(result, "test_tool")

    def test_hook_with_unsupported_event_name_raises_error(self):
        """Test that hook raises UnsupportedHookEventError for unsupported event."""

        def test_callback(data):
            return data

        test_data = {"hook_event_name": "Stop"}

        with self.assertRaises(UnsupportedHookEventError) as context:
            hook("UnsupportedEvent", test_data, test_callback)

        self.assertIn(
            "Unsupported hook event 'UnsupportedEvent'", str(context.exception)
        )

    def test_hook_with_invalid_callback_raises_error(self):
        """Test that hook raises CallbackError for invalid callback."""
        test_data = {"hook_event_name": "Stop"}

        with self.assertRaises(CallbackError) as context:
            hook("Stop", test_data, "not_callable")

        self.assertIn("Callback must be callable", str(context.exception))

    def test_hook_with_invalid_stdin_data_raises_error(self):
        """Test that hook raises InvalidDataError for invalid stdin data."""

        def test_callback(data):
            return data

        # Missing required hook_event_name field
        invalid_data = {"session_id": "test"}

        with self.assertRaises(InvalidDataError) as context:
            hook("Stop", invalid_data, test_callback)

        self.assertIn(
            "Hook data missing required field 'hook_event_name'", str(context.exception)
        )

    def test_hook_with_malformed_json_raises_error(self):
        """Test that hook raises InvalidDataError for malformed JSON."""

        def test_callback(data):
            return data

        malformed_json = '{"hook_event_name": "Stop", "invalid": json}'
        stdin_stream = StringIO(malformed_json)

        with self.assertRaises(InvalidDataError) as context:
            hook("Stop", stdin_stream, test_callback)

        self.assertIn("Invalid JSON in stdin", str(context.exception))

    def test_hook_with_event_mismatch_raises_error(self):
        """Test that hook raises HookEventMismatchError when events don't match."""

        def test_callback(data):
            return data

        test_data = {"hook_event_name": "PreToolUse", "tool_name": "test_tool"}

        with self.assertRaises(HookEventMismatchError) as context:
            hook("Stop", test_data, test_callback)

        expected_message = (
            "Hook event mismatch: requested 'Stop' but stdin contains 'PreToolUse'"
        )
        self.assertEqual(str(context.exception), expected_message)

    def test_hook_with_callback_exception_raises_callback_error(self):
        """Test that hook raises CallbackError when callback fails."""

        def failing_callback(data):
            raise ValueError("Callback failed")

        test_data = {"hook_event_name": "Stop"}

        with self.assertRaises(CallbackError) as context:
            hook("Stop", test_data, failing_callback)

        self.assertIn(
            "Callback execution failed: Callback failed", str(context.exception)
        )

    def test_hook_with_all_supported_events(self):
        """Test hook function with all supported event types."""

        def test_callback(data):
            return f"Event: {data['hook_event_name']}"

        supported_events = [
            "PreToolUse",
            "PostToolUse",
            "Notification",
            "Stop",
            "SubagentStop",
            "UserPromptSubmit",
            "PreCompact",
            "SessionStart",
        ]

        for event_name in supported_events:
            test_data = {"hook_event_name": event_name}
            result = hook(event_name, test_data, test_callback)
            self.assertEqual(result, f"Event: {event_name}")

    def test_hook_with_complex_data_structure(self):
        """Test hook function with complex nested data structure."""

        def test_callback(data):
            return {
                "processed": True,
                "original_event": data["hook_event_name"],
                "tool_count": len(data.get("tools", [])),
            }

        complex_data = {
            "hook_event_name": "PreToolUse",
            "session_id": "complex_session",
            "tool_name": "complex_tool",
            "tool_input": {"param1": "value1", "param2": {"nested": "value"}},
            "tools": ["tool1", "tool2", "tool3"],
        }

        result = hook("PreToolUse", complex_data, test_callback)

        expected_result = {
            "processed": True,
            "original_event": "PreToolUse",
            "tool_count": 3,
        }
        self.assertEqual(result, expected_result)

    def test_hook_with_empty_json_stream_raises_error(self):
        """Test that hook raises InvalidDataError for empty JSON stream."""

        def test_callback(data):
            return data

        empty_stream = StringIO("")

        with self.assertRaises(InvalidDataError) as context:
            hook("Stop", empty_stream, test_callback)

        self.assertIn("stdin contains no data", str(context.exception))

    def test_hook_with_whitespace_only_json_stream_raises_error(self):
        """Test that hook raises InvalidDataError for whitespace-only JSON stream."""

        def test_callback(data):
            return data

        whitespace_stream = StringIO("   \n\t  ")

        with self.assertRaises(InvalidDataError) as context:
            hook("Stop", whitespace_stream, test_callback)

        self.assertIn("stdin contains no data", str(context.exception))

    def test_hook_preserves_callback_return_value_types(self):
        """Test that hook preserves different return value types from callback."""
        test_data = {"hook_event_name": "Stop"}

        # Test string return
        result = hook("Stop", test_data, lambda data: "string_result")
        self.assertEqual(result, "string_result")

        # Test integer return
        result = hook("Stop", test_data, lambda data: 42)
        self.assertEqual(result, 42)

        # Test list return
        result = hook("Stop", test_data, lambda data: [1, 2, 3])
        self.assertEqual(result, [1, 2, 3])

        # Test dict return
        result = hook("Stop", test_data, lambda data: {"key": "value"})
        self.assertEqual(result, {"key": "value"})

        # Test None return
        result = hook("Stop", test_data, lambda data: None)
        self.assertIsNone(result)

    def test_hook_integration_with_mock_callback(self):
        """Test hook function integration with mock callback."""
        mock_callback = Mock(return_value="mocked_result")

        test_data = {
            "hook_event_name": "SessionStart",
            "source": "test_source",
            "cwd": "/test/path",
        }

        result = hook("SessionStart", test_data, mock_callback)

        self.assertEqual(result, "mocked_result")
        mock_callback.assert_called_once_with(test_data)


if __name__ == "__main__":
    unittest.main()
