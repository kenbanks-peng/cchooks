import sys
import subprocess
import logging
from typing import Dict, Any
from kb_cchook import hook
from kb_cchook.constants import SUPPORTED_HOOK_EVENTS

# Setup logging to file
log_file = "/tmp/cchooks.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout),  # Keep stdout for compatibility
    ],
)


def session_start(data: Dict[str, Any]) -> None:
    logging.info("Claude Code session started")


def stop(data: Dict[str, Any]) -> None:
    try:
        subprocess.run(["afplay", "/System/Library/Sounds/Blow.aiff"], check=False)
    except Exception as e:
        logging.error(f"Error playing sound: {e}")


def user_prompt_submit(data: Dict[str, Any]) -> None:
    prompt_preview = data.get("prompt", "")[:100]
    logging.info(f"User prompt submitted: {prompt_preview}...")


def pre_tool_use(data: Dict[str, Any]) -> None:
    tool_name = data.get("tool_name", "unknown")
    logging.info(f"About to use tool: {tool_name}")


def post_tool_use(data: Dict[str, Any]) -> None:
    tool_name = data.get("tool_name", "unknown")
    success = data.get("success", False)
    status = "successfully" if success else "with errors"
    logging.info(f"Tool {tool_name} completed {status}")


def notification(data: Dict[str, Any]) -> None:
    message = data.get("message", "")
    logging.info(f"Notification: {message}")


def pre_compact(data: Dict[str, Any]) -> None:
    logging.info("Memory compaction starting")


def subagent_stop(data: Dict[str, Any]) -> None:
    logging.info("Subagent stopped")


# Event handler lookup table
EVENT_HANDLERS = {
    "SessionStart": session_start,
    "Stop": stop,
    "UserPromptSubmit": user_prompt_submit,
    "PreToolUse": pre_tool_use,
    "PostToolUse": post_tool_use,
    "Notification": notification,
    "PreCompact": pre_compact,
    "SubagentStop": subagent_stop,
}


def callback(data: Dict[str, Any]) -> None:
    event_name = data.get("hook_event_name")
    logging.info(f"Hook triggered: {event_name}")

    handler = EVENT_HANDLERS.get(event_name)
    if handler:
        handler(data)

    # Log additional metadata if present
    if "metadata" in data:
        logging.info(f"Additional metadata: {data['metadata']}")


def main():
    if len(sys.argv) != 2:
        sys.exit(1)

    event_name = sys.argv[1]

    if event_name not in SUPPORTED_HOOK_EVENTS:
        logging.warning(f"Unsupported hook event '{event_name}'")
        sys.exit(1)

    try:
        # Pass stdin directly to the hook function (it expects a file-like object)
        hook(event_name, sys.stdin, callback)
    except Exception as e:
        logging.error(f"Error processing hook '{event_name}': {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
