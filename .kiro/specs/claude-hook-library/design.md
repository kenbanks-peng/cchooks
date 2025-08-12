# Design Document

## Overview

The Claude Hook Library (cchooks) is designed as a simplified, user-friendly Python library that abstracts the complexity of the Claude code hook specification. The library provides a single entry point function that handles all the protocol details internally, allowing developers to focus on their hook logic rather than the underlying implementation.

The design builds upon the existing hook architecture but simplifies the API to a single function call: `hook(hook_event_name, stdin, callback)`. This approach eliminates the need for developers to understand JSON parsing, event matching, or the Claude hook protocol specifics.

## Architecture

### Core Components

1. **Hook Function (`hook`)**: The main entry point that accepts three parameters and orchestrates the entire hook processing pipeline
2. **Event Validator**: Validates hook event names against supported Claude hook events
3. **Data Processor**: Handles stdin data parsing and validation according to Claude hook specification
4. **Callback Manager**: Manages callback execution with proper error handling and context
5. **Error Handler**: Provides comprehensive error handling with descriptive messages

### Library Structure

```
src/hooks/
├── __init__.py          # Main entry point, exports hook function
├── core.py              # Core hook processing logic
├── validators.py        # Event and data validation
├── exceptions.py        # Custom exception classes
└── constants.py         # Supported hook events and constants
```

### Data Flow

1. User calls `hook(hook_event_name, stdin, callback)`
2. Event Validator checks if hook_event_name is supported
3. Data Processor parses and validates stdin data
4. System checks if the event in stdin matches the requested hook_event_name
5. If match, Callback Manager executes the user's callback with processed data
6. Results are returned to the user with appropriate error handling

## Components and Interfaces

### Main Hook Function

```python
def hook(hook_event_name: str, stdin: Union[Dict[str, Any], TextIO], callback: Callable[[Dict[str, Any]], Any]) -> Any:
    """
    Process a Claude hook event with the provided callback.
    
    Args:
        hook_event_name: The Claude hook event name (e.g., 'Stop', 'PreToolUse')
        stdin: Either a dictionary containing hook data or a TextIO stream with JSON data
        callback: Function to execute when the hook event matches
        
    Returns:
        The return value from the callback function
        
    Raises:
        UnsupportedHookEventError: If hook_event_name is not supported
        InvalidDataError: If stdin data is malformed or invalid
        CallbackError: If callback execution fails
        HookEventMismatchError: If stdin event doesn't match hook_event_name
    """
```

### Event Validator

```python
class EventValidator:
    """Validates hook event names against supported Claude events."""
    
    SUPPORTED_EVENTS = {
        'PreToolUse', 'PostToolUse', 'Notification', 'Stop', 
        'SubagentStop', 'UserPromptSubmit', 'PreCompact', 'SessionStart'
    }
    
    @classmethod
    def validate_event_name(cls, event_name: str) -> None:
        """Validate that the event name is supported."""
        
    @classmethod
    def get_supported_events(cls) -> Set[str]:
        """Return set of all supported event names."""
```

### Data Processor

```python
class DataProcessor:
    """Handles parsing and validation of stdin data."""
    
    @staticmethod
    def process_stdin(stdin: Union[Dict[str, Any], TextIO]) -> Dict[str, Any]:
        """
        Process stdin data into a validated dictionary.
        
        Args:
            stdin: Either a dict or TextIO containing JSON data
            
        Returns:
            Validated dictionary containing hook event data
            
        Raises:
            InvalidDataError: If data is malformed or missing required fields
        """
        
    @staticmethod
    def validate_hook_data(data: Dict[str, Any]) -> None:
        """Validate that hook data contains required fields."""
```

### Callback Manager

```python
class CallbackManager:
    """Manages callback execution with error handling."""
    
    @staticmethod
    def execute_callback(callback: Callable, data: Dict[str, Any]) -> Any:
        """
        Execute the user's callback with proper error handling.
        
        Args:
            callback: The user-provided callback function
            data: Processed hook event data
            
        Returns:
            The callback's return value
            
        Raises:
            CallbackError: If callback execution fails
        """
        
    @staticmethod
    def validate_callback(callback: Any) -> None:
        """Validate that the callback is callable."""
```

## Data Models

### Hook Event Data Structure

The library expects stdin data to conform to the Claude hook specification:

```python
@dataclass
class HookEventData:
    """Standard structure for Claude hook event data."""
    hook_event_name: str
    session_id: Optional[str] = None
    # Additional fields vary by event type
    
    # PreToolUse specific
    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    
    # Stop specific
    stop_hook_active: Optional[bool] = None
    
    # SessionStart specific
    source: Optional[str] = None
    cwd: Optional[str] = None
```

### Custom Exception Hierarchy

```python
class CCHooksError(Exception):
    """Base exception for all cchooks errors."""
    pass

class UnsupportedHookEventError(CCHooksError):
    """Raised when an unsupported hook event name is provided."""
    pass

class InvalidDataError(CCHooksError):
    """Raised when stdin data is malformed or invalid."""
    pass

class CallbackError(CCHooksError):
    """Raised when callback execution fails."""
    pass

class HookEventMismatchError(CCHooksError):
    """Raised when stdin event doesn't match requested hook_event_name."""
    pass
```

## Error Handling

### Validation Errors

- **UnsupportedHookEventError**: Thrown when `hook_event_name` is not in the supported events list
- **InvalidDataError**: Thrown when stdin data cannot be parsed or is missing required fields
- **CallbackError**: Thrown when the user's callback function fails during execution
- **HookEventMismatchError**: Thrown when the event in stdin data doesn't match the requested `hook_event_name`

### Error Messages

All error messages will be descriptive and actionable:

```python
# Example error messages
"Unsupported hook event 'InvalidEvent'. Supported events: PreToolUse, PostToolUse, ..."
"Invalid stdin data: missing required field 'hook_event_name'"
"Callback execution failed: callback must be callable, got <class 'str'>"
"Hook event mismatch: requested 'Stop' but stdin contains 'PreToolUse'"
```

### Logging

The library will use Python's standard logging module with configurable levels:

- **DEBUG**: Detailed processing information
- **INFO**: General processing status
- **WARNING**: Non-fatal issues
- **ERROR**: Error conditions that prevent processing

## Testing Strategy

### Unit Tests

1. **Event Validation Tests**
   - Test all supported event names are accepted
   - Test unsupported event names raise appropriate errors
   - Test case sensitivity handling

2. **Data Processing Tests**
   - Test valid JSON parsing from TextIO
   - Test dictionary input handling
   - Test malformed data error handling
   - Test missing required fields

3. **Callback Execution Tests**
   - Test successful callback execution
   - Test callback return value handling
   - Test callback exception handling
   - Test non-callable callback validation

4. **Integration Tests**
   - Test complete hook processing flow
   - Test event matching logic
   - Test error propagation

### Test Data

Create comprehensive test fixtures covering:
- All supported hook event types
- Valid and invalid JSON structures
- Various callback function types
- Edge cases and error conditions

### Mock Strategy

Use Python's `unittest.mock` to:
- Mock TextIO streams for stdin testing
- Mock callback functions for execution testing
- Mock JSON parsing for error condition testing

## Implementation Notes

### Backward Compatibility

The library is designed to be compatible with the existing Claude hook specification without requiring changes to the Claude system. It acts as a client library that processes the same JSON data format.

### Performance Considerations

- Lazy loading of validation rules
- Efficient JSON parsing with error recovery
- Minimal memory footprint for data processing
- Fast event name validation using sets

### Extensibility

The design allows for future extension:
- Additional hook event types can be added to `SUPPORTED_EVENTS`
- Custom validators can be plugged into the validation pipeline
- Additional data processors can be added for specialized event types

### Dependencies

Minimal external dependencies:
- Python 3.7+ (for type hints and dataclasses)
- Standard library only (json, logging, typing, io)
- No third-party packages required