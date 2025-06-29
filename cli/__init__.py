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
OUTPUT_DIR = os.path.join(APP_DIR, "output")

KEY_DIRS = (APP_DIR, OUTPUT_DIR, LOG_DIR)

LOG_PATH = os.path.join(
    LOG_DIR,
    f"{datetime.now().date()}.log"
)

# Common formatter for file logs
file_formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# File handler
file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8", mode='a')
file_handler.setLevel(logging.DEBUG)  # File handler logs DEBUG and above
file_handler.setFormatter(file_formatter)


# Console handler with a custom filter
class InfoFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.INFO


console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)  # Console handler logs INFO and above
console_handler.addFilter(InfoFilter())  # Only allow INFO level logs
console_handler.setFormatter(logging.Formatter(fmt="%(message)s"))

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[file_handler, console_handler],
)

logger = logging.getLogger()

for directory in KEY_DIRS:
    logger.debug(f"Creating directory {directory}")
    os.makedirs(directory, exist_ok=True)

logger.info("All key directories created")
