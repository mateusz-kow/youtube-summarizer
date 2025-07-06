import argparse
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def get_args():
    """
    Parse and validate command-line arguments for the summarization CLI.

    Returns:
        argparse.Namespace: Parsed arguments including:
            - input_path (Path): Path to the input file or directory (must exist).
            - output_path (Path): Path to the output directory (will be created if not exists).
            - verbose (bool): Flag to enable verbose logging.

    Raises:
        argparse.ArgumentTypeError: If the provided paths are invalid or do not meet requirements.
    """

    parser = argparse.ArgumentParser(
        description="YouTube Summarizer CLI - Summarize YouTube videos from input files or directories."
    )

    parser.add_argument(
        "-u",
        "--url",
        required=True,
        type=str,
        help="URL of a youtube video to summarize.",
    )

    parser.add_argument(
        "-o",
        "--output-file",
        required=False,
        default=None,
        type=str,
        help="Path to output directory where summaries will be saved.",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging output."
    )

    args = parser.parse_args()
    return args
