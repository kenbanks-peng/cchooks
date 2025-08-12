#!/usr/bin/env python3
"""
Comprehensive test suite for the Claude Code Hooks Library.

This module provides comprehensive integration tests, test fixtures for all supported
hook event types, and tests for edge cases and error conditions.
"""

import json
import unittest
from unittest.mock import Mock
from io import StringIO, TextIOBase
from typing import Dict, Any

from src.hooks import hook
from src.hooks.exceptions import (
    UnsupportedHookEventError,
    InvalidDataError,
    CallbackError,
    HookEventMismatchError,
)
from src.hooks.constants import SUPPORTED_HOOK_EVENTS


class HookEventFixtures:
    """Test fixtures for all supported Claude hook event types."""

    @staticmethod
    def get_pretooluse_fixture() -> Dict[str, Any]:
        """Get test fixture for PreToolUse event."""
        return {
            "hook_event_name": "PreToolUse",
            "session_id": "test-session-123",
            "tool_name": "ReadFile",
            "tool_input": {"file_path": "/path/to/file.txt", "encoding": "utf-8"},
            "context": {"user_id": "user123", "workspace": "/workspace"},
        }

    @staticmethod
    def get_posttooluse_fixture() -> Dict[str, Any]:
        """Get test fixture for PostToolUse event."""
        return {
            "hook_event_name": "PostToolUse",
            "session_id": "test-session-123",
            "tool_name": "WriteFile",
            "tool_input": {
                "file_path": "/path/to/output.txt",
                "content": "Hello, World!",
            },
            "tool_output": {"success": True, "bytes_written": 13},
            "execution_time_ms": 45,
        }

    @staticmethod
    def get_notification_fixture() -> Dict[str, Any]:
        """Get test fixture for Notification event."""
        return {
            "hook_event_name": "Notification",
            "session_id": "test-session-123",
            "notification_type": "info",
            "message": "Task completed successfully",
            "timestamp": "2024-01-15T10:30:00Z",
            "metadata": {"task_id": "task-456", "duration": "2.5s"},
        }

    @staticmethod
    def get_stop_fixture() -> Dict[str, Any]:
        """Get test fixture for Stop event."""
        return {
            "hook_event_name": "Stop",
            "session_id": "test-session-123",
            "stop_hook_active": True,
            "reason": "user_requested",
            "final_state": {"tasks_completed": 5, "errors": 0},
        }

    @staticmethod
    def get_subagentstop_fixture() -> Dict[str, Any]:
        """Get test fixture for SubagentStop event."""
        return {
            "hook_event_name": "SubagentStop",
            "session_id": "test-session-123",
            "subagent_id": "subagent-789",
            "parent_agent_id": "agent-456",
            "completion_status": "success",
            "results": {
                "output": "Subagent task completed",
                "metrics": {"execution_time": 1.2},
            },
        }

    @staticmethod
    def get_userpromptsubmit_fixture() -> Dict[str, Any]:
        """Get test fixture for UserPromptSubmit event."""
        return {
            "hook_event_name": "UserPromptSubmit",
            "session_id": "test-session-123",
            "prompt_text": "Please analyze this code",
            "prompt_id": "prompt-321",
            "user_context": {
                "current_file": "main.py",
                "selection": {"start": 10, "end": 25},
            },
        }

    @staticmethod
    def get_precompact_fixture() -> Dict[str, Any]:
        """Get test fixture for PreCompact event."""
        return {
            "hook_event_name": "PreCompact",
            "session_id": "test-session-123",
            "compact_reason": "memory_limit",
            "current_memory_usage": "85%",
            "messages_to_compact": 150,
            "estimated_savings": "40%",
        }

    @staticmethod
    def get_sessionstart_fixture() -> Dict[str, Any]:
        """Get test fixture for SessionStart event."""
        return {
            "hook_event_name": "SessionStart",
            "session_id": "test-session-123",
            "source": "vscode_extension",
            "cwd": "/home/user/project",
            "user_info": {
                "user_id": "user123",
                "preferences": {"theme": "dark", "language": "en"},
            },
            "environment": {"os": "linux", "python_version": "3.9.0"},
        }

    @classmethod
    def get_all_fixtures(cls) -> Dict[str, Dict[str, Any]]:
        """Get all test fixtures as a dictionary keyed by event name."""
        return {
            "PreToolUse": cls.get_pretooluse_fixture(),
            "PostToolUse": cls.get_posttooluse_fixture(),
            "Notification": cls.get_notification_fixture(),
            "Stop": cls.get_stop_fixture(),
            "SubagentStop": cls.get_subagentstop_fixture(),
            "UserPromptSubmit": cls.get_userpromptsubmit_fixture(),
            "PreCompact": cls.get_precompact_fixture(),
            "SessionStart": cls.get_sessionstart_fixture(),
        }

    @classmethod
    def get_minimal_fixtures(cls) -> Dict[str, Dict[str, Any]]:
        """Get minimal test fixtures with only required fields."""
        return {
            event_name: {"hook_event_name": event_name}
            for event_name in SUPPORTED_HOOK_EVENTS
        }


class MockObjects:
    """Factory for creating mock objects for testing."""

    @staticmethod
    def create_mock_textio(content: str) -> Mock:
        """Create a mock TextIO object with specified content."""
        mock_textio = Mock(spec=TextIOBase)
        mock_textio.read.return_value = content
        return mock_textio

    @staticmethod
    def create_failing_textio(exception: Exception) -> Mock:
        """Create a mock TextIO object that raises an exception on read."""
        mock_textio = Mock(spec=TextIOBase)
        mock_textio.read.side_effect = exception
        return mock_textio

    @staticmethod
    def create_mock_callback(return_value: Any = None) -> Mock:
        """Create a mock callback function."""
        mock_callback = Mock(return_value=return_value)
        return mock_callback

    @staticmethod
    def create_failing_callback(exception: Exception) -> Mock:
        """Create a mock callback that raises an exception."""
        mock_callback = Mock(side_effect=exception)
        return mock_callback

    @staticmethod
    def create_non_callable_mock() -> Mock:
        """Create a mock object that is not callable."""
        mock_obj = Mock()
        # Remove the __call__ method to make it non-callable
        if hasattr(mock_obj, "__call__"):
            del mock_obj.__call__
        return mock_obj


class TestComprehensiveIntegration(unittest.TestCase):
    """Comprehensive integration tests for the hook library."""

    def setUp(self):
        """Set up test fixtures and mocks."""
        self.fixtures = HookEventFixtures()
        self.mock_factory = MockObjects()

    def test_all_supported_events_with_fixtures(self):
        """Test hook function with all supported event types using fixtures."""
        all_fixtures = self.fixtures.get_all_fixtures()

        for event_name in SUPPORTED_HOOK_EVENTS:
            with self.subTest(event_name=event_name):
                # Get fixture for this event
                fixture_data = all_fixtures.get(event_name)
                if not fixture_data:
                    # Use minimal fixture if specific one not available
                    fixture_data = {"hook_event_name": event_name}

                # Create callback that returns event name
                def test_callback(data):
                    return f"Processed: {data['hook_event_name']}"

                # Test with dictionary input
                result = hook(event_name, fixture_data, test_callback)
                self.assertEqual(result, f"Processed: {event_name}")

                # Test with TextIO input
                json_data = json.dumps(fixture_data)
                text_io = StringIO(json_data)
                result = hook(event_name, text_io, test_callback)
                self.assertEqual(result, f"Processed: {event_name}")

    def test_complex_callback_scenarios(self):
        """Test various callback scenarios with complex data processing."""
        test_data = self.fixtures.get_pretooluse_fixture()

        # Test callback that modifies and returns data
        def modifying_callback(data):
            result = data.copy()
            result["processed"] = True
            result["processing_time"] = 0.123
            return result

        result = hook("PreToolUse", test_data, modifying_callback)
        self.assertIn("processed", result)
        self.assertTrue(result["processed"])
        self.assertEqual(result["processing_time"], 0.123)

        # Test callback that returns different data types
        test_cases = [
            (lambda data: "string_result", "string_result"),
            (lambda data: 42, 42),
            (lambda data: [1, 2, 3], [1, 2, 3]),
            (lambda data: {"key": "value"}, {"key": "value"}),
            (lambda data: None, None),
            (lambda data: True, True),
        ]

        for callback, expected in test_cases:
            with self.subTest(expected_type=type(expected).__name__):
                result = hook("PreToolUse", test_data, callback)
                self.assertEqual(result, expected)

    def test_mock_callback_integration(self):
        """Test integration with mock callback objects."""
        test_data = self.fixtures.get_stop_fixture()

        # Test with mock callback
        mock_callback = self.mock_factory.create_mock_callback("mocked_result")
        result = hook("Stop", test_data, mock_callback)

        self.assertEqual(result, "mocked_result")
        mock_callback.assert_called_once_with(test_data)

        # Test with mock callback that has side effects
        side_effects = []

        def side_effect_callback(data):
            side_effects.append(data["hook_event_name"])
            return len(side_effects)

        mock_callback = Mock(side_effect=side_effect_callback)
        result = hook("Stop", test_data, mock_callback)

        self.assertEqual(result, 1)
        self.assertEqual(side_effects, ["Stop"])
        mock_callback.assert_called_once_with(test_data)

    def test_textio_mock_scenarios(self):
        """Test various TextIO mock scenarios."""
        test_data = self.fixtures.get_notification_fixture()
        json_content = json.dumps(test_data)

        # Test with mock TextIO
        mock_textio = self.mock_factory.create_mock_textio(json_content)

        def test_callback(data):
            return data["notification_type"]

        result = hook("Notification", mock_textio, test_callback)
        self.assertEqual(result, "info")
        mock_textio.read.assert_called_once()

        # Test with mock TextIO that returns empty content
        empty_mock = self.mock_factory.create_mock_textio("")

        with self.assertRaises(InvalidDataError) as context:
            hook("Notification", empty_mock, test_callback)

        self.assertIn("stdin contains no data", str(context.exception))

        # Test with mock TextIO that raises IOError
        failing_mock = self.mock_factory.create_failing_textio(IOError("Read failed"))

        with self.assertRaises(InvalidDataError) as context:
            hook("Notification", failing_mock, test_callback)

        self.assertIn("Error reading stdin", str(context.exception))


class TestEdgeCasesAndErrorConditions(unittest.TestCase):
    """Test edge cases and error conditions."""

    def setUp(self):
        """Set up test fixtures."""
        self.fixtures = HookEventFixtures()
        self.mock_factory = MockObjects()

    def test_boundary_conditions(self):
        """Test boundary conditions and edge cases."""
        # Test with very large JSON data
        large_data = self.fixtures.get_pretooluse_fixture()
        large_data["large_field"] = "x" * 10000  # 10KB string

        def test_callback(data):
            return len(data["large_field"])

        result = hook("PreToolUse", large_data, test_callback)
        self.assertEqual(result, 10000)

        # Test with deeply nested data
        nested_data = self.fixtures.get_posttooluse_fixture()
        nested_data["deep"] = {"level1": {"level2": {"level3": {"value": "deep"}}}}

        def nested_callback(data):
            return data["deep"]["level1"]["level2"]["level3"]["value"]

        result = hook("PostToolUse", nested_data, nested_callback)
        self.assertEqual(result, "deep")

        # Test with unicode and special characters
        unicode_data = self.fixtures.get_notification_fixture()
        unicode_data["message"] = "Hello 世界! 🌍 Special chars: àáâãäå"

        def unicode_callback(data):
            return data["message"]

        result = hook("Notification", unicode_data, unicode_callback)
        self.assertEqual(result, "Hello 世界! 🌍 Special chars: àáâãäå")

    def test_malformed_data_scenarios(self):
        """Test various malformed data scenarios."""

        def test_callback(data):
            return data

        # Test with JSON that's not an object
        malformed_cases = [
            '"just a string"',
            "123",
            "true",
            "null",
            '["array", "not", "object"]',
        ]

        for malformed_json in malformed_cases:
            with self.subTest(json_content=malformed_json):
                text_io = StringIO(malformed_json)

                with self.assertRaises(InvalidDataError) as context:
                    hook("Stop", text_io, test_callback)

                self.assertIn("Hook data must be a dictionary", str(context.exception))

    def test_callback_error_scenarios(self):
        """Test various callback error scenarios."""
        test_data = self.fixtures.get_stop_fixture()

        # Test callback that raises different exception types
        exception_cases = [
            ValueError("Value error in callback"),
            TypeError("Type error in callback"),
            KeyError("missing_key"),
            AttributeError("'dict' object has no attribute 'missing'"),
            RuntimeError("Runtime error in callback"),
            Exception("Generic exception"),
        ]

        for exception in exception_cases:
            with self.subTest(exception_type=type(exception).__name__):
                failing_callback = self.mock_factory.create_failing_callback(exception)

                with self.assertRaises(CallbackError) as context:
                    hook("Stop", test_data, failing_callback)

                self.assertIn("Callback execution failed", str(context.exception))
                self.assertIsInstance(context.exception.__cause__, type(exception))

    def test_non_callable_objects(self):
        """Test various non-callable objects as callbacks."""
        test_data = self.fixtures.get_stop_fixture()

        non_callable_objects = [
            "string",
            123,
            [1, 2, 3],
            {"key": "value"},
            None,
            True,
            False,
            object(),
        ]

        for non_callable in non_callable_objects:
            with self.subTest(object_type=type(non_callable).__name__):
                try:
                    hook("Stop", test_data, non_callable)
                    self.fail(
                        f"Expected CallbackError for non-callable {type(non_callable).__name__}"
                    )
                except CallbackError as e:
                    self.assertIn("Callback must be callable", str(e))
                except Exception as e:
                    self.fail(f"Expected CallbackError but got {type(e).__name__}: {e}")

    def test_event_name_edge_cases(self):
        """Test edge cases for event name validation."""
        test_data = self.fixtures.get_stop_fixture()

        def test_callback(data):
            return data

        # Test case sensitivity
        case_variations = [
            "stop",  # lowercase
            "STOP",  # uppercase
            "Stop",  # mixed case (only this should work)
            "sTop",  # mixed case
            "pretooluse",  # lowercase
            "PRETOOLUSE",  # uppercase
            "PreToolUse",  # correct case (should work)
        ]

        for event_name in case_variations:
            with self.subTest(event_name=event_name):
                if event_name in SUPPORTED_HOOK_EVENTS:
                    # Should work
                    try:
                        # Need to adjust test data to match
                        adjusted_data = test_data.copy()
                        adjusted_data["hook_event_name"] = event_name
                        result = hook(event_name, adjusted_data, test_callback)
                        self.assertIsNotNone(result)
                    except Exception as e:
                        self.fail(
                            f"Valid event name {event_name} should not raise exception: {e}"
                        )
                else:
                    # Should fail
                    with self.assertRaises(UnsupportedHookEventError):
                        hook(event_name, test_data, test_callback)

    def test_json_parsing_edge_cases(self):
        """Test edge cases in JSON parsing."""

        def test_callback(data):
            return data

        # Test various malformed JSON strings that should definitely fail
        malformed_json_cases = [
            '{"hook_event_name": "Stop",}',  # trailing comma
            '{"hook_event_name": "Stop" "extra": "value"}',  # missing comma
            '{"hook_event_name": "Stop", "unclosed": "string}',  # unclosed string
            '{hook_event_name: "Stop"}',  # unquoted key
            '{"hook_event_name": Stop}',  # unquoted value
            "",  # empty string
            "   ",  # whitespace only
            "\n\t\r",  # various whitespace
            "{",  # incomplete object
            "}",  # just closing brace
            "null",  # null value
            "undefined",  # undefined (not valid JSON)
        ]

        for malformed_json in malformed_json_cases:
            with self.subTest(json_content=repr(malformed_json)):
                text_io = StringIO(malformed_json)

                # The hook function should raise InvalidDataError for all these cases
                try:
                    hook("Stop", text_io, test_callback)
                    self.fail(
                        f"Expected InvalidDataError for malformed JSON: {repr(malformed_json)}"
                    )
                except InvalidDataError as e:
                    # Should contain appropriate error message
                    error_msg = str(e)
                    self.assertTrue(
                        "Invalid JSON" in error_msg
                        or "stdin contains no data" in error_msg
                        or "Hook data must be a dictionary" in error_msg,
                        f"Unexpected error message for {repr(malformed_json)}: {error_msg}",
                    )
                except Exception as e:
                    self.fail(
                        f"Expected InvalidDataError but got {type(e).__name__}: {e}"
                    )

        # Test case where JSON is valid but results in wrong data type
        non_dict_json_cases = [
            '"just a string"',
            "123",
            "true",
            '["array", "not", "object"]',
        ]

        for non_dict_json in non_dict_json_cases:
            with self.subTest(json_content=repr(non_dict_json)):
                text_io = StringIO(non_dict_json)

                try:
                    hook("Stop", text_io, test_callback)
                    self.fail(
                        f"Expected InvalidDataError for non-dict JSON: {repr(non_dict_json)}"
                    )
                except InvalidDataError as e:
                    self.assertIn("Hook data must be a dictionary", str(e))
                except Exception as e:
                    self.fail(
                        f"Expected InvalidDataError but got {type(e).__name__}: {e}"
                    )

        # Test valid JSON with duplicate keys (Python handles this, takes last value)
        duplicate_key_json = (
            '{"hook_event_name": "Stop", "duplicate": 1, "duplicate": 2}'
        )
        text_io = StringIO(duplicate_key_json)

        # This should actually work since Python's JSON parser handles duplicate keys
        try:
            result = hook("Stop", text_io, test_callback)
            # Should work and the duplicate key should have the last value
            self.assertEqual(result["duplicate"], 2)
        except Exception as e:
            self.fail(f"Valid JSON with duplicate keys should work: {e}")

    def test_memory_and_performance_edge_cases(self):
        """Test memory and performance related edge cases."""

        # Test with very large callback return values
        def large_return_callback(data):
            return {"large_data": "x" * 100000}  # 100KB return value

        test_data = self.fixtures.get_stop_fixture()
        result = hook("Stop", test_data, large_return_callback)
        self.assertEqual(len(result["large_data"]), 100000)

        # Test with callback that processes data multiple times
        def processing_intensive_callback(data):
            # Simulate intensive processing
            result = data.copy()
            for i in range(1000):
                result[f"processed_{i}"] = i * 2
            return len(result)

        result = hook("Stop", test_data, processing_intensive_callback)
        # The stop fixture has 5 original fields, so 5 + 1000 = 1005
        self.assertEqual(result, 1005)  # original fields + 1000 processed fields


class TestErrorMessageQuality(unittest.TestCase):
    """Test the quality and helpfulness of error messages."""

    def test_unsupported_event_error_messages(self):
        """Test that unsupported event error messages are helpful."""
        test_data = {"hook_event_name": "Stop"}

        def test_callback(data):
            return data

        with self.assertRaises(UnsupportedHookEventError) as context:
            hook("InvalidEvent", test_data, test_callback)

        error_msg = str(context.exception)

        # Should contain the invalid event name
        self.assertIn("InvalidEvent", error_msg)

        # Should contain suggestion with supported events
        self.assertIn("Use one of the supported events:", error_msg)

        # Should contain at least some supported events
        for event in list(SUPPORTED_HOOK_EVENTS)[:3]:
            self.assertIn(event, error_msg)

    def test_invalid_data_error_messages(self):
        """Test that invalid data error messages are helpful."""

        def test_callback(data):
            return data

        # Test missing hook_event_name
        invalid_data = {"session_id": "test", "other_field": "value"}

        with self.assertRaises(InvalidDataError) as context:
            hook("Stop", invalid_data, test_callback)

        error_msg = str(context.exception)
        self.assertIn("missing required field 'hook_event_name'", error_msg)
        self.assertIn("Available fields:", error_msg)
        self.assertIn("session_id", error_msg)
        self.assertIn("other_field", error_msg)

    def test_callback_error_messages(self):
        """Test that callback error messages are helpful."""
        test_data = {"hook_event_name": "Stop"}

        # Test non-callable callback
        with self.assertRaises(CallbackError) as context:
            hook("Stop", test_data, "not_callable")

        error_msg = str(context.exception)
        self.assertIn("Callback must be callable", error_msg)
        self.assertIn("got str", error_msg)

        # Test callback execution failure
        def failing_callback(data):
            raise ValueError("Custom error message")

        with self.assertRaises(CallbackError) as context:
            hook("Stop", test_data, failing_callback)

        error_msg = str(context.exception)
        self.assertIn("Callback execution failed", error_msg)
        self.assertIn("Custom error message", error_msg)

    def test_hook_event_mismatch_error_messages(self):
        """Test that hook event mismatch error messages are helpful."""
        test_data = {"hook_event_name": "PreToolUse"}

        def test_callback(data):
            return data

        with self.assertRaises(HookEventMismatchError) as context:
            hook("Stop", test_data, test_callback)

        error_msg = str(context.exception)
        self.assertIn("Hook event mismatch", error_msg)
        self.assertIn("requested 'Stop'", error_msg)
        self.assertIn("stdin contains 'PreToolUse'", error_msg)


if __name__ == "__main__":
    # Create a test suite with all test classes
    test_classes = [
        TestComprehensiveIntegration,
        TestEdgeCasesAndErrorConditions,
        TestErrorMessageQuality,
    ]

    suite = unittest.TestSuite()

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)
