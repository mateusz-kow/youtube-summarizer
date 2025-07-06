import os.path
from dotenv import load_dotenv
from platformdirs import user_data_dir, user_log_dir

load_dotenv()

APP_NAME = "youtube-summarizer"
AUTHOR = "mateusz_kow"

APP_DIR = user_data_dir(APP_NAME, AUTHOR)
LOG_DIR = user_log_dir(APP_NAME, AUTHOR)
OUTPUT_DIR = os.path.join(APP_DIR, "Output")

try:
    from ytsum.local_config import *
except ImportError as e:
    pass

KEY_DIRS = (APP_DIR, OUTPUT_DIR, LOG_DIR)

for directory in KEY_DIRS:
    os.makedirs(directory, exist_ok=True)
