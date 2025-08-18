import logging
from typing import Dict, Any


def pre_compact(data: Dict[str, Any]) -> None:
    logging.info("Memory compaction starting")