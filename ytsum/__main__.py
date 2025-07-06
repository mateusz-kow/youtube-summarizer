import logging
import os
import re
import sys

from ytsum import APP_NAME, OUTPUT_DIR
from ytsum.llms.gemini import Gemini
from ytsum.youtube.youtube_manager import get_video_subtitles, get_video_name
from ytsum.utils.input_parser import get_args
from ytsum.utils.prompts.prompt_factory import Prompt


logger = logging.getLogger(__name__)


def sanitize_filename(name: str, replacement: str = "") -> str:
    """
    Sanitizes a filename by removing characters not allowed in Windows, macOS, or Linux filesystems.

    Args:
        name (str): Proposed filename.
        replacement (str): Character to replace forbidden characters with (default: empty string).

    Returns:
        str: A sanitized, filesystem-safe filename.
    """
    forbidden_chars = r'[<>:"/\\|?*\x00-\x1F]'
    sanitized = re.sub(forbidden_chars, replacement, name)
    sanitized = sanitized.strip(" .")
    return sanitized[:255]


def main() -> None:
    """
    Executes the end-to-end process of retrieving subtitles from a YouTube video,
    saving the transcript, generating a summary using an LLM, and writing the output
    to structured markdown files.

    Workflow:
        1. Parse the video URL from CLI arguments.
        2. Retrieve the video title and sanitize it for filesystem safety.
        3. Create an output directory using the sanitized title.
        4. Fetch subtitles for the given video.
        5. Save the full transcript as a markdown file.
        6. Generate a summary of the transcript using the Gemini LLM.
        7. Save the summary as a markdown file.
        8. Output the summary to standard output.

    Raises:
        RuntimeError: If subtitles cannot be retrieved.
        Exception: For any unexpected error during processing.
    """
    logger.info(f"Starting {APP_NAME}")

    try:
        video_url = get_args()

        video_title = get_video_name(video_url)
        safe_title = sanitize_filename(video_title)
        output_dir = os.path.join(OUTPUT_DIR, safe_title)
        os.makedirs(output_dir, exist_ok=True)

        subtitles = get_video_subtitles(video_url)
        if not subtitles:
            raise RuntimeError(f"Failed to retrieve subtitles from video: {video_url}")

        text_path = os.path.join(output_dir, "text.md")
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(subtitles + f"\n\nOriginal video: [**{video_title}**]({video_url})")
        logger.info(f"Transcript saved to: {text_path}")

        llm = Gemini()
        summary = llm.ask_prompt(Prompt.SUMMARY, subtitles)
        summary_text = (
            summary + f"\n\nOriginal video: [**{video_title}**]({video_url})\n"
        )

        summary_path = os.path.join(output_dir, "summary.md")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary_text)
        logger.info(f"Summary saved to: {summary_path}")

        sys.stdout.write(summary_text)

    except Exception as e:
        logger.exception("An error occurred during execution.")
        print(f"Error: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
