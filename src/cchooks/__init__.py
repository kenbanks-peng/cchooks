"""
Claude Code Hooks Library (cchooks)

A simplified Python library for integrating with Claude's code hook system.
Provides a clean API for registering and handling hook events.

Usage:
    from cchooks import hook

    def my_callback(data):
        print(f"Hook event received: {data}")
        return "processed"

    result = hook("Stop", stdin_data, my_callback)

Example:
    >>> from cchooks import hook
    >>>
    >>> def simple_callback(data):
    ...     return f"Processed {data['hook_event_name']}"
    >>>
    >>> hook_data = {"hook_event_name": "Stop", "session_id": "123"}
    >>> result = hook("Stop", hook_data, simple_callback)
    >>> print(result)  # "Processed Stop"

For more examples, see the examples/ directory.
"""

from .core import hook

# Library metadata
__version__ = "0.1.0"
__author__ = "Claude Code Hooks Library Contributors"
__description__ = (
    "A simplified Python library for integrating with Claude's code hook system"
)
__license__ = "MIT"

# Public API - main entry point
__all__ = ["hook"]
