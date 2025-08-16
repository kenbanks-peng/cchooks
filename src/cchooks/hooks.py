import sys
from typing import Dict, Any, Callable
from kb_cchook import hook
from kb_cchook.constants import SUPPORTED_HOOK_EVENTS


def claude_code_hook_callback(data: Dict[str, Any]) -> None:
    """
    Default callback function for Claude Code hooks.
    Processes hook data and performs appropriate actions based on the event type.
    """
    event_name = data.get("hook_event_name")
    
    print(f"Hook triggered: {event_name}")
    
    # Handle different hook events
    if event_name == "SessionStart":
        print("Claude Code session started")
    elif event_name == "Stop":
        print("Claude Code session ended")
    elif event_name == "UserPromptSubmit":
        print(f"User prompt submitted: {data.get('prompt', '')[:100]}...")
    elif event_name == "PreToolUse":
        tool_name = data.get("tool_name", "unknown")
        print(f"About to use tool: {tool_name}")
    elif event_name == "PostToolUse":
        tool_name = data.get("tool_name", "unknown")
        success = data.get("success", False)
        print(f"Tool {tool_name} completed {'successfully' if success else 'with errors'}")
    elif event_name == "Notification":
        print(f"Notification: {data.get('message', '')}")
    elif event_name == "PreCompact":
        print("Memory compaction starting")
    elif event_name == "SubagentStop":
        print("Subagent stopped")
    
    # Log additional data if present
    if "metadata" in data:
        print(f"Additional metadata: {data['metadata']}")


def create_hook_handler(custom_callback: Callable[[Dict[str, Any]], None] = None) -> Callable[[str], None]:
    """
    Creates a hook handler function that can be used for any Claude Code hook event.
    
    Args:
        custom_callback: Optional custom callback function to use instead of the default
        
    Returns:
        A function that can handle hook events
    """
    callback = custom_callback or claude_code_hook_callback
    
    def hook_handler(event_name: str) -> None:
        """Handle a specific hook event"""
        if event_name not in SUPPORTED_HOOK_EVENTS:
            print(f"Warning: Unsupported hook event '{event_name}'", file=sys.stderr)
            return
            
        try:
            # Pass stdin directly to the hook function (it expects a file-like object)
            hook(event_name, sys.stdin, callback)
        except Exception as e:
            print(f"Error processing hook '{event_name}': {e}", file=sys.stderr)
            sys.exit(1)
    
    return hook_handler


def main():
    """Main entry point for the hook script"""
    if len(sys.argv) != 2:
        print("Usage: cchooks <hook_event_name>", file=sys.stderr)
        print(f"Supported events: {', '.join(sorted(SUPPORTED_HOOK_EVENTS))}", file=sys.stderr)
        sys.exit(1)
    
    event_name = sys.argv[1]
    hook_handler = create_hook_handler()
    hook_handler(event_name)


if __name__ == "__main__":
    main()
