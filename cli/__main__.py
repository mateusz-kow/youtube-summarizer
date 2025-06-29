import logging
import sys

from cli import APP_NAME, OUTPUT_DIR
from cli.llms.gemini import Gemini
from cli.youtube.youtube_manager import get_video_subtitles, get_video_name
from cli.utils.input_parser import get_args
from cli.utils.prompts.prompt_factory import Prompt

import re
import os


def sanitize_filename(name: str, replacement: str = "") -> str:
    """
    Sanityzuje nazwę pliku, usuwając niedozwolone znaki dla systemów Windows, macOS, Linux.
    :param name: Proponowana nazwa pliku
    :param replacement: Znak, którym zastąpić niedozwolone znaki
    :return: Poprawna, bezpieczna nazwa pliku
    """
    forbidden_chars = r'[<>:"/\\|?*\x00-\x1F]'
    name = re.sub(forbidden_chars, replacement, name)
    name = name.strip(" .")

    return name[:255]


logger = logging.getLogger(__name__)
logger.info(f"Starting {APP_NAME}")

try:
    video_url = get_args()

    name = get_video_name(video_url)
    output_dir = os.path.join(OUTPUT_DIR, sanitize_filename(name))
    os.makedirs(output_dir, exist_ok=True)

    text = get_video_subtitles(video_url)
    if not text:
        raise RuntimeError(f"Failed to get subtitles from video {video_url}")
    with open(os.path.join(output_dir, "text.md"), 'w', encoding="utf-8") as file:
        file.write(text + f"\n\nOriginal video: [**{name}**]({video_url})")
    logger.info(f"Text saved to {output_dir}{os.sep}text.md")

    llm = Gemini()
    summary = llm.ask_prompt(Prompt.SUMMARY, text)
    adjusted_summary = summary + f"\n\nOriginal video: [**{name}**]({video_url})\n"
    with open(os.path.join(output_dir, "summary.md"), 'w', encoding="utf-8") as file:
        file.write(adjusted_summary)
    logger.info(f"Summary saved to {output_dir}{os.sep}summary.md")

    sys.stdout.write(adjusted_summary)

except Exception as e:
    logger.exception(e)
    print(f"{e}", file=sys.stderr)
