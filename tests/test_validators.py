"""
Unit tests for the validators module of the Claude Code Hooks Library.

This module tests event validation and data processing functionality.
"""

import json
import unittest
from unittest.mock import MagicMock
from io import StringIO

from src.hooks.validators import EventValidator, DataProcessor
from src.hooks.exceptions import UnsupportedHookEventError, InvalidDataError
from src.hooks.constants import SUPPORTED_HOOK_EVENTS


class TestEventValidator(unittest.TestCase):
    """Test cases for the EventValidator class."""

    def test_validate_event_name_with_valid_events(self):
        """Test that valid event names pass validation."""
        # Test each supported event
        for event_name in SUPPORTED_HOOK_EVENTS:
            with self.subTest(event_name=event_name):
                # Should not raise any exception
                EventValidator.validate_event_name(event_name)

    def test_validate_event_name_with_invalid_event(self):
        """Test that invalid event names raise UnsupportedHookEventError."""
        invalid_events = ["InvalidEvent", "UnknownHook", "BadEventName", "NotSupported"]

        for invalid_event in invalid_events:
            with self.subTest(invalid_event=invalid_event):
                with self.assertRaises(UnsupportedHookEventError) as context:
                    EventValidator.validate_event_name(invalid_event)

                # Check that error message contains the invalid event name
                self.assertIn(invalid_event, str(context.exception))
                # Check that error message contains supported events
                self.assertIn(
                    "Use one of the supported events:", str(context.exception)
                )

    def test_validate_event_name_with_non_string_input(self):
        """Test that non-string inputs raise UnsupportedHookEventError."""
        non_string_inputs = [123, None, [], {}, True, False]

        for non_string_input in non_string_inputs:
            with self.subTest(input_type=type(non_string_input).__name__):
                with self.assertRaises(UnsupportedHookEventError) as context:
                    EventValidator.validate_event_name(non_string_input)

                # Check that error message mentions the type issue
                self.assertIn("must be a string", str(context.exception))
                self.assertIn(type(non_string_input).__name__, str(context.exception))

    def test_validate_event_name_case_sensitivity(self):
        """Test that event name validation is case sensitive."""
        # Test lowercase versions of valid events should fail
        for event_name in SUPPORTED_HOOK_EVENTS:
            lowercase_event = event_name.lower()
            if lowercase_event != event_name:  # Only test if actually different
                with self.subTest(event_name=lowercase_event):
                    with self.assertRaises(UnsupportedHookEventError):
                        EventValidator.validate_event_name(lowercase_event)

    def test_get_supported_events_returns_correct_set(self):
        """Test that get_supported_events returns the correct set of events."""
        supported_events = EventValidator.get_supported_events()

        # Should return the same events as defined in constants
        self.assertEqual(supported_events, SUPPORTED_HOOK_EVENTS)

        # Should be a set
        self.assertIsInstance(supported_events, set)

    def test_get_supported_events_returns_copy(self):
        """Test that get_supported_events returns a copy, not the original."""
        supported_events = EventValidator.get_supported_events()

        # Modify the returned set
        original_length = len(supported_events)
        supported_events.add("TestEvent")

        # Get a fresh copy
        fresh_copy = EventValidator.get_supported_events()

        # Fresh copy should not be affected by modifications to the first copy
        self.assertEqual(len(fresh_copy), original_length)
        self.assertNotIn("TestEvent", fresh_copy)

    def test_error_message_format_for_unsupported_event(self):
        """Test that error messages are properly formatted and informative."""
        invalid_event = "TestInvalidEvent"

        with self.assertRaises(UnsupportedHookEventError) as context:
            EventValidator.validate_event_name(invalid_event)

        error_message = str(context.exception)

        # Should contain the invalid event name
        self.assertIn(invalid_event, error_message)

        # Should contain "Unsupported hook event"
        self.assertIn("Unsupported hook event", error_message)

        # Should contain supported events information
        self.assertIn("Use one of the supported events:", error_message)

        # Should contain at least some of the supported events
        for event in list(SUPPORTED_HOOK_EVENTS)[:3]:  # Check first 3 events
            self.assertIn(event, error_message)

    def test_supported_events_are_not_empty(self):
        """Test that there are actually supported events defined."""
        supported_events = EventValidator.get_supported_events()
        self.assertGreater(len(supported_events), 0)

        # Verify some expected events are present
        expected_events = {"PreToolUse", "PostToolUse", "Stop", "SessionStart"}
        self.assertTrue(expected_events.issubset(supported_events))


class TestDataProcessor(unittest.TestCase):
    """Test cases for the DataProcessor class."""

    def test_process_stdin_with_valid_dict(self):
        """Test processing stdin when input is a valid dictionary."""
        valid_data = {
            "hook_event_name": "Stop",
            "session_id": "test-session",
            "stop_hook_active": True,
        }

        result = DataProcessor.process_stdin(valid_data)
        self.assertEqual(result, valid_data)

    def test_process_stdin_with_valid_json_string(self):
        """Test processing stdin when input is a TextIO with valid JSON."""
        valid_data = {
            "hook_event_name": "PreToolUse",
            "session_id": "test-session",
            "tool_name": "test_tool",
        }
        json_string = json.dumps(valid_data)
        text_io = StringIO(json_string)

        result = DataProcessor.process_stdin(text_io)
        self.assertEqual(result, valid_data)

    def test_process_stdin_with_invalid_json(self):
        """Test that invalid JSON raises InvalidDataError."""
        invalid_json = '{"hook_event_name": "Stop", "invalid": json}'
        text_io = StringIO(invalid_json)

        with self.assertRaises(InvalidDataError) as context:
            DataProcessor.process_stdin(text_io)

        self.assertIn("Invalid JSON in stdin", str(context.exception))

    def test_process_stdin_with_empty_textio(self):
        """Test that empty TextIO raises InvalidDataError."""
        empty_io = StringIO("")

        with self.assertRaises(InvalidDataError) as context:
            DataProcessor.process_stdin(empty_io)

        self.assertIn("stdin contains no data", str(context.exception))

    def test_process_stdin_with_whitespace_only_textio(self):
        """Test that TextIO with only whitespace raises InvalidDataError."""
        whitespace_io = StringIO("   \n\t  ")

        with self.assertRaises(InvalidDataError) as context:
            DataProcessor.process_stdin(whitespace_io)

        self.assertIn("stdin contains no data", str(context.exception))

    def test_process_stdin_with_none_input(self):
        """Test that None input raises InvalidDataError."""
        with self.assertRaises(InvalidDataError) as context:
            DataProcessor.process_stdin(None)

        self.assertIn("stdin cannot be None", str(context.exception))

    def test_process_stdin_with_invalid_type(self):
        """Test that invalid input types raise InvalidDataError."""
        invalid_inputs = ["string", 123, [], True, False]

        for invalid_input in invalid_inputs:
            with self.subTest(input_type=type(invalid_input).__name__):
                with self.assertRaises(InvalidDataError) as context:
                    DataProcessor.process_stdin(invalid_input)

                self.assertIn(
                    "stdin must be a dictionary or TextIO object",
                    str(context.exception),
                )
                self.assertIn(type(invalid_input).__name__, str(context.exception))

    def test_process_stdin_with_textio_read_error(self):
        """Test that TextIO read errors are handled properly."""
        mock_textio = MagicMock()
        mock_textio.read.side_effect = IOError("Read error")

        with self.assertRaises(InvalidDataError) as context:
            DataProcessor.process_stdin(mock_textio)

        self.assertIn("Error reading stdin", str(context.exception))

    def test_validate_hook_data_with_valid_data(self):
        """Test that valid hook data passes validation."""
        valid_data = {"hook_event_name": "Stop", "session_id": "test-session"}

        # Should not raise any exception
        DataProcessor.validate_hook_data(valid_data)

    def test_validate_hook_data_missing_hook_event_name(self):
        """Test that missing hook_event_name raises InvalidDataError."""
        invalid_data = {"session_id": "test-session", "other_field": "value"}

        with self.assertRaises(InvalidDataError) as context:
            DataProcessor.validate_hook_data(invalid_data)

        self.assertIn(
            "missing required field 'hook_event_name'", str(context.exception)
        )

    def test_validate_hook_data_non_string_hook_event_name(self):
        """Test that non-string hook_event_name raises InvalidDataError."""
        invalid_types = [123, None, [], {}, True, False]

        for invalid_type in invalid_types:
            with self.subTest(hook_event_type=type(invalid_type).__name__):
                invalid_data = {
                    "hook_event_name": invalid_type,
                    "session_id": "test-session",
                }

                with self.assertRaises(InvalidDataError) as context:
                    DataProcessor.validate_hook_data(invalid_data)

                self.assertIn(
                    "'hook_event_name' must be a string", str(context.exception)
                )
                self.assertIn(type(invalid_type).__name__, str(context.exception))

    def test_validate_hook_data_empty_hook_event_name(self):
        """Test that empty hook_event_name raises InvalidDataError."""
        empty_names = ["", "   ", "\n\t"]

        for empty_name in empty_names:
            with self.subTest(empty_name=repr(empty_name)):
                invalid_data = {
                    "hook_event_name": empty_name,
                    "session_id": "test-session",
                }

                with self.assertRaises(InvalidDataError) as context:
                    DataProcessor.validate_hook_data(invalid_data)

                self.assertIn(
                    "'hook_event_name' cannot be empty", str(context.exception)
                )

    def test_validate_hook_data_non_dict_input(self):
        """Test that non-dictionary input raises InvalidDataError."""
        invalid_inputs = ["string", 123, [], None, True, False]

        for invalid_input in invalid_inputs:
            with self.subTest(input_type=type(invalid_input).__name__):
                with self.assertRaises(InvalidDataError) as context:
                    DataProcessor.validate_hook_data(invalid_input)

                self.assertIn("Hook data must be a dictionary", str(context.exception))
                self.assertIn(type(invalid_input).__name__, str(context.exception))

    def test_process_stdin_validates_data(self):
        """Test that process_stdin calls validate_hook_data internally."""
        # Test with dict input missing required field
        invalid_dict = {"session_id": "test"}

        with self.assertRaises(InvalidDataError) as context:
            DataProcessor.process_stdin(invalid_dict)

        self.assertIn(
            "missing required field 'hook_event_name'", str(context.exception)
        )

        # Test with TextIO input missing required field
        invalid_json = '{"session_id": "test"}'
        text_io = StringIO(invalid_json)

        with self.assertRaises(InvalidDataError) as context:
            DataProcessor.process_stdin(text_io)

        self.assertIn(
            "missing required field 'hook_event_name'", str(context.exception)
        )

    def test_process_stdin_with_complex_valid_data(self):
        """Test processing stdin with complex but valid hook data."""
        complex_data = {
            "hook_event_name": "PreToolUse",
            "session_id": "complex-session-123",
            "tool_name": "complex_tool",
            "tool_input": {
                "param1": "value1",
                "param2": 42,
                "nested": {"key": "value"},
            },
            "additional_field": ["list", "of", "values"],
        }

        # Test with dict
        result_dict = DataProcessor.process_stdin(complex_data)
        self.assertEqual(result_dict, complex_data)

        # Test with TextIO
        json_string = json.dumps(complex_data)
        text_io = StringIO(json_string)
        result_textio = DataProcessor.process_stdin(text_io)
        self.assertEqual(result_textio, complex_data)


if __name__ == "__main__":
    unittest.main()
