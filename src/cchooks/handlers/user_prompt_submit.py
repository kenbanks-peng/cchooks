import logging
from typing import Dict, Any


def user_prompt_submit(data: Dict[str, Any]) -> None:
    prompt_preview = data.get("prompt", "")[:100]
    logging.info(f"User prompt submitted: {prompt_preview}...")