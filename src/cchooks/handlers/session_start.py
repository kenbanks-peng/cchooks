import logging
from typing import Dict, Any


def session_start(data: Dict[str, Any]) -> None:
    logging.info("Claude Code session started")