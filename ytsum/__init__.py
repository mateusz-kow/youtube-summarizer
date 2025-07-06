import sys
from datetime import datetime

import os
import logging
from dotenv import load_dotenv
from platformdirs import user_data_dir, user_log_dir

load_dotenv()

APP_NAME = "youtube-summarizer"
AUTHOR = "mateusz_kow"

APP_DIR = user_data_dir(APP_NAME, AUTHOR)
LOG_DIR = user_log_dir(APP_NAME, AUTHOR)
OUTPUT_DIR = os.path.join(APP_DIR, "Output")

KEY_DIRS = (APP_DIR, OUTPUT_DIR, LOG_DIR)

for directory in KEY_DIRS:
    os.makedirs(directory, exist_ok=True)

LOG_PATH = os.path.join(LOG_DIR, f"{datetime.now().date()}.log")

# Common formatter for file logs
file_formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

# File handler logs DEBUG and above to the log file
file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8", mode="a")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(file_formatter)


class InfoFilter(logging.Filter):
    """Logging filter that only allows INFO level log records."""

    def filter(self, record):
        """Return True only if the log record level is INFO."""
        return record.levelno == logging.INFO


# Console handler logs only INFO level to stdout with simple message formatting
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.addFilter(InfoFilter())
console_handler.setFormatter(logging.Formatter(fmt="%(message)s"))

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[file_handler, console_handler],
)

logger = logging.getLogger()
