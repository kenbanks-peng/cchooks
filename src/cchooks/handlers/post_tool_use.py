import logging
from typing import Dict, Any


def post_tool_use(data: Dict[str, Any]) -> None:
    tool_name = data.get("tool_name", "unknown")
    success = data.get("success", False)
    status = "successfully" if success else "with errors"
    logging.info(f"Tool {tool_name} completed {status}")