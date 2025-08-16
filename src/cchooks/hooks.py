import sys
import subprocess
from typing import Dict, Any, Callable
from kb_cchook import hook
from kb_cchook.constants import SUPPORTED_HOOK_EVENTS


def callback(data: Dict[str, Any]) -> None:
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
        try:
            subprocess.run(["afplay", "/System/Library/Sounds/Blow.aiff"], check=False)
        except Exception as e:
            print(f"Error playing sound: {e}")
    elif event_name == "UserPromptSubmit":
        print(f"User prompt submitted: {data.get('prompt', '')[:100]}...")
    elif event_name == "PreToolUse":
        tool_name = data.get("tool_name", "unknown")
        print(f"About to use tool: {tool_name}")
    elif event_name == "PostToolUse":
        tool_name = data.get("tool_name", "unknown")
        success = data.get("success", False)
        print(
            f"Tool {tool_name} completed {'successfully' if success else 'with errors'}"
        )
    elif event_name == "Notification":
        print(f"Notification: {data.get('message', '')}")
    elif event_name == "PreCompact":
        print("Memory compaction starting")
    elif event_name == "SubagentStop":
        print("Subagent stopped")

    # Log additional data if present
    if "metadata" in data:
        print(f"Additional metadata: {data['metadata']}")


def main():
    if len(sys.argv) != 2:
        sys.exit(1)

    event_name = sys.argv[1]

    if event_name not in SUPPORTED_HOOK_EVENTS:
        print(f"Warning: Unsupported hook event '{event_name}'", file=sys.stderr)
        sys.exit(1)

    try:
        # Pass stdin directly to the hook function (it expects a file-like object)
        hook(event_name, sys.stdin, callback)
    except Exception as e:
        print(f"Error processing hook '{event_name}': {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
