import logging
import os
import sys
from datetime import datetime

from ytsum.config import LOG_DIR

LOG_PATH = os.path.join(LOG_DIR, f"{datetime.now().date()}.log")


def configure_logging(verbose: bool = False) -> None:
    """
    Configure application-wide logging.

    Sets up logging to a daily rotating log file and optionally to the console.
    - Logs of level DEBUG and above are written to a log file located at `LOG_DIR/YYYY-MM-DD.log`.
    - If `verbose` is True, INFO-level messages are also printed to stdout with simplified formatting.

    This function ensures that:
    - File logging always includes timestamps, log levels, and messages.
    - Console output (if enabled) is minimal and user-friendly.
    - NLTK's internal logging is suppressed to prevent unnecessary output.

    Args:
        verbose (bool): If True, enables console output for INFO-level messages.

    Returns:
        None
    """
    # Common formatter for file logs
    file_formatter = logging.Formatter(fmt="%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    # File handler logs DEBUG and above to the log file
    file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8", mode="a")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    handlers: list[logging.Handler] = [file_handler]

    if verbose:

        class InfoFilter(logging.Filter):
            """Logging filter that only allows INFO level log records."""

            def filter(self, record: logging.LogRecord) -> bool:
                """Return True only if the log record level is INFO."""
                return bool(record.levelno == logging.INFO)

        # Console handler logs only INFO level to stdout with simple message formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.addFilter(InfoFilter())
        console_handler.setFormatter(logging.Formatter(fmt="%(message)s"))
        handlers.append(console_handler)

    logging.basicConfig(
        level=logging.DEBUG,
        handlers=handlers,
    )
