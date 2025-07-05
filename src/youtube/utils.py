import re
import logging


logger = logging.getLogger(__name__)


def get_raw_text_from_srt(srt_subs: str) -> str:
    """
    Parses SRT subtitle content and returns clean text:
    - Removes indices and timestamps
    - Strips annotations like [music], [applause]
    - Preserves multi-line dialogue as single lines
    """
    logger.debug(f"Parsing srt subtitles: {srt_subs}")
    blocks = srt_subs.strip().split("\n\n")
    lines = []

    for block in blocks:
        parts = block.strip().splitlines()

        if len(parts) < 3:
            continue

        text_lines = [line for line in parts[2:] if line.strip()]
        cleaned = [
            re.sub(r"\[.*?]", "", line).strip()
            for line in text_lines
        ]

        block_text = " ".join(filter(None, cleaned))
        if block_text:
            lines.append(block_text)

    subtitles = " ".join(lines)
    logger.debug(f"Srt subtitles parsed as {subtitles}")

    return subtitles
