import logging
import subprocess
from typing import Dict, Any


def stop(data: Dict[str, Any]) -> None:
    try:
        logging.info(f"Stop handler called with data: {data}")
        subprocess.run(["afplay", "/System/Library/Sounds/Blow.aiff"], check=False)
    except Exception as e:
        logging.error(f"Error playing sound: {e}")
