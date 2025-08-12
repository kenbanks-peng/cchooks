# Design Document

## Overview

The generic hook handler will be a single function that abstracts the common pattern of reading JSON from stdin, parsing it, checking the event type, and conditionally executing a callback. This design will replace the current monolithic approach with a more modular and reusable system.

The current system has a main function that maps event names to specific handler functions. The new design will invert this relationship - instead of the main function knowing about all handlers, each handler will use the generic function to process its specific event type.

## Architecture

### Current Architecture
```
main() -> get_event() -> handlers[event_name](data)
```

### New Architecture
```
generic_handler(target_event, stdin, callback) -> callback(data) if event matches
```

### Core Components

1. **Generic Handler Function**: The main processing function that handles JSON parsing and event filtering
2. **Event Processing Logic**: Centralized logic for reading and validating JSON input
3. **Callback Interface**: Standardized interface for event-specific processing
4. **Error Handling**: Centralized error handling for common failure scenarios

## Components and Interfaces

### Generic Handler Function

```python
def process_hook_event(
    target_hook_event_name: str,
    stdin: TextIO,
    callback: Callable[[Dict[str, Any]], int]
) -> Dict[str, Any]:
    """
    Generic handler for processing hook events.
    
    Args:
        target_hook_event_name: The specific event name to handle
        stdin: Input stream containing JSON data
        callback: Function to call if event matches target
        
    Returns:
        Dict containing the parsed JSON data
        
    Raises:
        Exception: If JSON parsing fails or input is invalid
    """
```

### Callback Interface

All callback functions must conform to this interface:
```python
CallbackFunction = Callable[[Dict[str, Any]], int]
```

Where:
- Input: Dictionary containing the parsed JSON data
- Output: Integer return code (0 for success, non-zero for error)

### Data Flow

1. **Input Validation**: Check if stdin has data available
2. **JSON Parsing**: Parse the JSON input into a Python dictionary
3. **Data Validation**: Ensure the parsed data is a dictionary with required fields
4. **Event Matching**: Compare the hook_event_name in data with target_hook_event_name
5. **Callback Execution**: If events match, execute the callback with the data
6. **Return Data**: Return the parsed data dictionary regardless of callback execution

## Data Models

### Input Data Structure
```python
{
    "hook_event_name": str,  # Required: The type of hook event
    "tool_name": str,        # Optional: Name of the tool being used
    "tool_input": dict,      # Optional: Input parameters for the tool
    "tool_response": dict,   # Optional: Response from tool execution
    "message": str,          # Optional: Notification message
    "session_id": str,       # Optional: Session identifier
    # ... other event-specific fields
}
```

### Return Value
The function returns the complete parsed data dictionary, allowing callers to access all event data even if the callback wasn't executed.

## Error Handling

### Exception Types and Handling

1. **No Input Data**: When stdin is a TTY or empty
   - Raise: `Exception("No input data provided")`
   - Occurs when the function is called without piped input

2. **Invalid JSON**: When JSON parsing fails
   - Raise: `json.JSONDecodeError` (let it bubble up with original message)
   - Occurs when input contains malformed JSON

3. **Wrong Data Type**: When parsed JSON is not a dictionary
   - Raise: `Exception(f"Expected JSON object, got {type(input_data).__name__}")`
   - Occurs when input is valid JSON but not an object

4. **Missing Event Name**: When hook_event_name is not in data
   - Log warning and skip callback execution
   - Return the data dictionary normally
   - This is not considered a fatal error

5. **Callback Exceptions**: When the callback function raises an exception
   - Let callback exceptions bubble up to the caller
   - The caller (usually main()) should handle callback-specific errors

### Error Recovery Strategy

- **Graceful Degradation**: Missing optional fields should not cause failures
- **Clear Error Messages**: All exceptions should provide actionable error information
- **Logging Integration**: Use existing logging system for warnings and debug info
- **Backward Compatibility**: Maintain same error behavior as current system

## Testing Strategy

### Unit Tests

1. **Happy Path Testing**
   - Test successful event matching and callback execution
   - Test successful parsing with various valid JSON inputs
   - Test return value contains correct data

2. **Event Filtering Testing**
   - Test that callback is not called when events don't match
   - Test that data is still returned when events don't match
   - Test case sensitivity of event name matching

3. **Error Condition Testing**
   - Test behavior with invalid JSON input
   - Test behavior with non-dictionary JSON
   - Test behavior with missing hook_event_name
   - Test behavior with TTY stdin

4. **Callback Integration Testing**
   - Test that callback receives correct data structure
   - Test that callback return values are preserved
   - Test that callback exceptions are properly propagated

### Integration Tests

1. **Migration Testing**
   - Test that existing handlers work with new generic function
   - Test that all current event types are properly handled
   - Test that logging and error handling remain consistent

2. **Performance Testing**
   - Ensure no significant performance regression
   - Test with large JSON payloads
   - Test with high-frequency event processing

### Mock Testing Strategy

- Use `io.StringIO` to mock stdin input
- Use mock callbacks to verify call patterns
- Use pytest fixtures for common test data scenarios

## Migration Plan

### Phase 1: Create Generic Handler
1. Implement the `process_hook_event` function
2. Add comprehensive unit tests
3. Ensure backward compatibility with existing data structures

### Phase 2: Refactor Individual Handlers
1. Update each handler file to use the generic function
2. Remove duplicate JSON parsing code
3. Maintain existing handler function signatures for compatibility

### Phase 3: Update Main Function
1. Simplify main() function to use generic handler pattern
2. Remove the handlers dictionary mapping
3. Update error handling to work with new architecture

### Phase 4: Cleanup
1. Remove unused utility functions (like get_event)
2. Update documentation and examples
3. Add integration tests for the complete system