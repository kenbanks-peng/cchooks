import logging
from typing import Dict, Any


def subagent_stop(data: Dict[str, Any]) -> None:
    logging.info("Subagent stopped")