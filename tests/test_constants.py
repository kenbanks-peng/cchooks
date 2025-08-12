#!/usr/bin/env python3
"""
Unit tests for the Claude Code Hooks Library constants.

This module tests the constants defined in src/hooks/constants.py.
"""

import pytest
from src.hooks.constants import SUPPORTED_HOOK_EVENTS


class TestSupportedHookEvents:
    """Test the SUPPORTED_HOOK_EVENTS constant."""

    def test_supported_hook_events_is_set(self):
        """Test that SUPPORTED_HOOK_EVENTS is a set."""
        assert isinstance(SUPPORTED_HOOK_EVENTS, set)

    def test_supported_hook_events_not_empty(self):
        """Test that SUPPORTED_HOOK_EVENTS is not empty."""
        assert len(SUPPORTED_HOOK_EVENTS) > 0

    def test_supported_hook_events_contains_expected_events(self):
        """Test that SUPPORTED_HOOK_EVENTS contains all expected Claude hook events."""
        expected_events = {
            "PreToolUse",
            "PostToolUse",
            "Notification",
            "Stop",
            "SubagentStop",
            "UserPromptSubmit",
            "PreCompact",
            "SessionStart",
        }

        assert SUPPORTED_HOOK_EVENTS == expected_events

    def test_supported_hook_events_contains_pretooluse(self):
        """Test that PreToolUse is in supported events."""
        assert "PreToolUse" in SUPPORTED_HOOK_EVENTS

    def test_supported_hook_events_contains_posttooluse(self):
        """Test that PostToolUse is in supported events."""
        assert "PostToolUse" in SUPPORTED_HOOK_EVENTS

    def test_supported_hook_events_contains_notification(self):
        """Test that Notification is in supported events."""
        assert "Notification" in SUPPORTED_HOOK_EVENTS

    def test_supported_hook_events_contains_stop(self):
        """Test that Stop is in supported events."""
        assert "Stop" in SUPPORTED_HOOK_EVENTS

    def test_supported_hook_events_contains_subagentstop(self):
        """Test that SubagentStop is in supported events."""
        assert "SubagentStop" in SUPPORTED_HOOK_EVENTS

    def test_supported_hook_events_contains_userpromptsubmit(self):
        """Test that UserPromptSubmit is in supported events."""
        assert "UserPromptSubmit" in SUPPORTED_HOOK_EVENTS

    def test_supported_hook_events_contains_precompact(self):
        """Test that PreCompact is in supported events."""
        assert "PreCompact" in SUPPORTED_HOOK_EVENTS

    def test_supported_hook_events_contains_sessionstart(self):
        """Test that SessionStart is in supported events."""
        assert "SessionStart" in SUPPORTED_HOOK_EVENTS

    def test_supported_hook_events_case_sensitive(self):
        """Test that hook event names are case sensitive."""
        # These should not be in the set (wrong case)
        assert "pretooluse" not in SUPPORTED_HOOK_EVENTS
        assert "PRETOOLUSE" not in SUPPORTED_HOOK_EVENTS
        assert "stop" not in SUPPORTED_HOOK_EVENTS
        assert "STOP" not in SUPPORTED_HOOK_EVENTS

    def test_supported_hook_events_no_invalid_events(self):
        """Test that invalid/unsupported events are not in the set."""
        invalid_events = {"InvalidEvent", "UnknownHook", "TestEvent", "CustomHook"}

        for invalid_event in invalid_events:
            assert invalid_event not in SUPPORTED_HOOK_EVENTS

    def test_supported_hook_events_count(self):
        """Test that we have exactly the expected number of supported events."""
        assert len(SUPPORTED_HOOK_EVENTS) == 8


if __name__ == "__main__":
    pytest.main([__file__])
