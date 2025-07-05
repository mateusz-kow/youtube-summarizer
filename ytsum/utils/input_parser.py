import argparse
import logging

logger = logging.getLogger(__name__)


def get_args():
    """
    Parses command-line arguments for the summarization CLI.
    """
    logger.info("Parsing command-line arguments")

    parser = argparse.ArgumentParser(
        description="Generate an AI-powered summary of a YouTube video"
    )

    parser.add_argument("--url", type=str, help="URL of the YouTube video to summarize")

    args = parser.parse_args()

    logger.info(f"Received arguments: url='{args.url}'")
    return args.url
