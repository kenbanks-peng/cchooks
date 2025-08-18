import logging
from typing import Dict, Any


def notification(data: Dict[str, Any]) -> None:
    message = data.get("message", "")
    logging.info(f"Notification: {message}")