import logging
import platform
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

APP_NAME = "snortamv"
OS_TYPE = platform.system().lower()

# -------- Paths --------
if OS_TYPE == "windows":
    BASE_DIR = Path.cwd()
    LOG_DIR = BASE_DIR / "logStore" / "errors"
elif OS_TYPE == "linux":
    LOG_DIR = Path("/var/log/snortamv")
else:
    print("Unsupported OS")
    sys.exit(1)

LOG_DIR.mkdir(parents=True, exist_ok=True)
ERROR_LOG = LOG_DIR / "snortamv_error.log"


# -------- Error Logger Factory --------
def get_error_logger(name: str = APP_NAME) -> logging.Logger:
    logger = logging.getLogger(f"{APP_NAME}.error.{name}")

    if logger.handlers:
        return logger

    logger.setLevel(logging.ERROR)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler = RotatingFileHandler(
        ERROR_LOG, maxBytes=5 * 1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False

    return logger
