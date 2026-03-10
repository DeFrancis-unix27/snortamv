import logging
import platform
import os
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

APP_NAME = "snortamv"
OS_TYPE = platform.system().lower()

# ---------------- Paths ----------------
if OS_TYPE == "windows":
    BASE_DIR = Path.cwd()
    LOG_DIR = BASE_DIR / "logStore" / "logs"
elif OS_TYPE == "linux":
    LOG_DIR = Path("/var/log/snortamv")
else:
    print("Unsupported OS")
    sys.exit(1)

LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "snortamv.log"

# ---------------- Logging Setup ----------------
LOG_LEVEL = logging.INFO  

formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

file_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5  # 5MB
)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logging.basicConfig(
    level=LOG_LEVEL,
    handlers=[file_handler, console_handler],
)


def get_logger(name: str = APP_NAME) -> logging.Logger:
    return logging.getLogger(name)
