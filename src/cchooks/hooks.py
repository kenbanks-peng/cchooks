import sys
import logging
from typing import Dict, Any
from kb_cchook import hook
from kb_cchook.constants import SUPPORTED_HOOK_EVENTS

from .handlers.session_start import session_start
from .handlers.stop import stop
from .handlers.user_prompt_submit import user_prompt_submit
from .handlers.pre_tool_use import pre_tool_use
from .handlers.post_tool_use import post_tool_use
from .handlers.notification import notification
from .handlers.pre_compact import pre_compact
from .handlers.subagent_stop import subagent_stop

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
