import logging
from typing import Dict, Any


def pre_tool_use(data: Dict[str, Any]) -> None:
    tool_name = data.get("tool_name", "unknown")
    logging.info(f"About to use tool: {tool_name}")