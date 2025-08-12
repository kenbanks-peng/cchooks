# Claude Code Hooks Library (cchooks)

A simplified Python library for integrating with Claude's code hook system. This library provides a clean, easy-to-use API for registering and handling hook events without needing to understand the underlying Claude hook specification details.

## Features

- **Simple API**: Single function entry point for all hook events
- **Comprehensive Error Handling**: Descriptive error messages with suggestions
- **Type Safety**: Full type hints and validation
- **Flexible Input**: Supports both dictionary and JSON stream input
- **Extensive Documentation**: Complete examples and API documentation
- **Zero Dependencies**: Uses only Python standard library

## Installation

### From Source

```bash
# Clone the repository
git clone <repository-url>
cd claude-hook-library

# Install in development mode
pip install -e .
```

### Using pip (when published)

```bash
pip install cchooks
```

## Quick Start

```python
from cchooks import hook

def my_callback(data):
    """Handle the hook event data."""
    event_name = data.get("hook_event_name")
    print(f"Received {event_name} event")
    return f"Processed {event_name}"

# Hook event data (normally from Claude via stdin)
hook_data = {
    "hook_event_name": "Stop",
    "session_id": "session_123",
    "stop_hook_active": False
}

# Process the hook event
try:
    result = hook("Stop", hook_data, my_callback)
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {e}")
```

## API Reference

### Main Function

#### `hook(hook_event_name, stdin, callback)`

Process a Claude hook event with the provided callback.

**Parameters:**
- `hook_event_name` (str): The Claude hook event name (e.g., 'Stop', 'PreToolUse')
- `stdin` (Union[Dict[str, Any], TextIO]): Either a dictionary containing hook data or a TextIO stream with JSON data
- `callback` (Callable[[Dict[str, Any]], Any]): Function to execute when the hook event matches

**Returns:**
- The return value from the callback function

**Raises:**
- `UnsupportedHookEventError`: If hook_event_name is not supported
- `InvalidDataError`: If stdin data is malformed or invalid
- `CallbackError`: If callback execution fails
- `HookEventMismatchError`: If stdin event doesn't match hook_event_name

### Supported Hook Events

The library supports all standard Claude hook events:

- `PreToolUse`: Before a tool is executed
- `PostToolUse`: After a tool is executed
- `Notification`: For notification events
- `Stop`: When a session stops
- `SubagentStop`: When a subagent stops
- `UserPromptSubmit`: When user submits a prompt
- `PreCompact`: Before conversation compacting
- `SessionStart`: When a session starts

### Exception Classes

All exceptions inherit from `CCHooksError` and include helpful error messages and suggestions:

- `CCHooksError`: Base exception for all library errors
- `UnsupportedHookEventError`: Unsupported hook event name
- `InvalidDataError`: Malformed or invalid stdin data
- `CallbackError`: Callback execution failure
- `HookEventMismatchError`: Event name mismatch between request and data

## Usage Examples

### Basic Usage

```python
from cchooks import hook

def simple_handler(data):
    event_name = data.get("hook_event_name")
    print(f"Handling {event_name} event")
    return {"status": "processed", "event": event_name}

# Dictionary input
data = {"hook_event_name": "Stop", "session_id": "123"}
result = hook("Stop", data, simple_handler)
```

### JSON Stream Input

```python
import json
import io
from cchooks import hook

def stream_handler(data):
    return f"Processed {data['hook_event_name']}"

# JSON stream input (simulating stdin)
json_data = json.dumps({
    "hook_event_name": "PreToolUse",
    "tool_name": "Read",
    "tool_input": {"file_path": "example.txt"}
})
stream = io.StringIO(json_data)

result = hook("PreToolUse", stream, stream_handler)
```

### Error Handling

```python
from cchooks import hook
from cchooks.exceptions import CCHooksError, UnsupportedHookEventError

def error_handler(data):
    return "success"

try:
    result = hook("InvalidEvent", {"hook_event_name": "Stop"}, error_handler)
except UnsupportedHookEventError as e:
    print(f"Unsupported event: {e}")
    print(f"Supported events: {e.supported_events}")
except CCHooksError as e:
    print(f"Library error: {e}")
    if e.suggestion:
        print(f"Suggestion: {e.suggestion}")
```

### Class-Based Callbacks

```python
from cchooks import hook

class HookProcessor:
    def __init__(self):
        self.processed_count = 0
    
    def process_event(self, data):
        self.processed_count += 1
        event_name = data.get("hook_event_name")
        return {
            "event": event_name,
            "count": self.processed_count,
            "status": "processed"
        }

processor = HookProcessor()
data = {"hook_event_name": "Notification", "message": "Test"}
result = hook("Notification", data, processor.process_event)
```

### Real Hook Script Example

```python
#!/usr/bin/env python3
"""
Example hook script that reads from stdin and processes hook events.
This is how you would use the library in an actual Claude hook script.
"""

import sys
import json
from cchooks import hook

def handle_pre_tool_use(data):
    """Handle PreToolUse events with security validation."""
    tool_name = data.get("tool_name", "")
    
    # Block dangerous tools
    if tool_name in ["rm", "sudo", "chmod"]:
        return {
            "permission": "denied",
            "reason": f"Tool '{tool_name}' is blocked for security"
        }
    
    # Allow safe tools
    return {
        "permission": "granted",
        "reason": f"Tool '{tool_name}' is allowed"
    }

def main():
    try:
        # Process hook event from stdin
        result = hook("PreToolUse", sys.stdin, handle_pre_tool_use)
        
        # Output result (Claude will read this)
        print(json.dumps(result))
        return 0
        
    except Exception as e:
        print(f"Hook processing failed: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

## Advanced Usage

### Security Validation

```python
from cchooks import hook

class SecurityValidator:
    def __init__(self):
        self.blocked_tools = {"rm", "sudo", "chmod"}
        self.sensitive_paths = {"/etc", "/root", "~/.ssh"}
    
    def validate_tool(self, data):
        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})
        
        # Check for blocked tools
        if any(blocked in tool_name.lower() for blocked in self.blocked_tools):
            return {"permission": "denied", "reason": "Blocked tool"}
        
        # Check for sensitive paths
        file_path = tool_input.get("file_path", "")
        if any(sensitive in file_path for sensitive in self.sensitive_paths):
            return {"permission": "review_required", "reason": "Sensitive path"}
        
        return {"permission": "granted", "reason": "Safe operation"}

validator = SecurityValidator()
data = {
    "hook_event_name": "PreToolUse",
    "tool_name": "Read",
    "tool_input": {"file_path": "/home/user/file.txt"}
}

result = hook("PreToolUse", data, validator.validate_tool)
```

### Development Workflow Integration

```python
from cchooks import hook

class WorkflowManager:
    def __init__(self):
        self.session_files = {}
    
    def track_session_start(self, data):
        session_id = data.get("session_id")
        cwd = data.get("cwd", "")
        
        self.session_files[session_id] = {
            "working_directory": cwd,
            "files_modified": [],
            "start_time": "now"
        }
        
        return {
            "session_initialized": True,
            "working_directory": cwd,
            "tracking_enabled": True
        }
    
    def track_file_changes(self, data):
        session_id = data.get("session_id")
        tool_input = data.get("tool_input", {})
        file_path = tool_input.get("file_path", "")
        
        if session_id in self.session_files and file_path:
            self.session_files[session_id]["files_modified"].append(file_path)
        
        return {
            "file_tracked": file_path,
            "session_id": session_id
        }

manager = WorkflowManager()

# Track session start
session_data = {
    "hook_event_name": "SessionStart",
    "session_id": "dev_123",
    "cwd": "/home/user/project"
}
hook("SessionStart", session_data, manager.track_session_start)

# Track file modifications
file_data = {
    "hook_event_name": "PreToolUse",
    "tool_name": "Write",
    "tool_input": {"file_path": "src/main.py"},
    "session_id": "dev_123"
}
hook("PreToolUse", file_data, manager.track_file_changes)
```

## Examples

The `src/examples/` directory contains comprehensive examples:

- `basic_usage.py`: Simple usage patterns and common scenarios
- `advanced_callbacks.py`: Complex callback implementations and class-based handlers
- `error_handling.py`: Comprehensive error handling examples
- `real_world_usage.py`: Practical use cases and integration patterns

Run examples:

```bash
python src/examples/basic_usage.py
python src/examples/advanced_callbacks.py
python src/examples/error_handling.py
python src/examples/real_world_usage.py
```

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest

# Run specific test files
python -m pytest test_core.py
python -m pytest test_validators.py
python -m pytest test_exceptions.py

# Run with coverage
python -m pytest --cov=src/hooks
```

## Development

### Setting up Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd claude-hook-library

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest pytest-cov black isort mypy
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Type checking
mypy src/

# Run tests
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass (`pytest`)
6. Format your code (`black src/`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### Version 0.1.0

- Initial release
- Core hook processing functionality
- Support for all Claude hook events
- Comprehensive error handling
- Full documentation and examples
- Complete test suite

## Support

For questions, issues, or contributions:

1. Check the [examples](src/examples/) for usage patterns
2. Review the [API documentation](#api-reference)
3. Open an issue on GitHub for bugs or feature requests
4. Refer to the Claude hook specification for event details

## Acknowledgments

- Built for integration with Claude's code hook system
- Inspired by the need for simplified hook event processing
- Thanks to the Claude development team for the hook specification