"""
Constants and configuration values for the Claude Code Hooks Library.

This module contains supported hook events and other constant values.
"""

from typing import Set


# Supported Claude hook events based on the Claude hook specification
SUPPORTED_HOOK_EVENTS: Set[str] = {
    "PreToolUse",
    "PostToolUse",
    "Notification",
    "Stop",
    "SubagentStop",
    "UserPromptSubmit",
    "PreCompact",
    "SessionStart",
}
