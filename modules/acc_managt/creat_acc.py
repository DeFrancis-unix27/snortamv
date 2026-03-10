# modules/acc_managt/create_acc.py
from pathlib import Path
from database.db import create_account, get_account
from modules.utilities.error_handler import get_error_logger
from modules.utilities.logger import get_logger
logger = get_logger(__name__)
errorLogger = get_error_logger(__name__)
def create_account_cli(root: Path):
    username = input("Enter username: ").strip()
    if get_account(username):
        print(f"User already exists")
        logger.info(f"{username} already exists")
        return
    fullname = input("Full name: ").strip()
    password = input("Password: ").strip()
    ok = create_account(username, fullname, password)
    if ok:
        print(f"Created account: {username}")
        logger.info(f"Created account: {username}")
    else:
        print("Failed to create account (maybe user exists).")
        errorLogger.exception("Failed to create account (maybe user exists).")
    return ok

if __name__ == "__main__":
    create_account_cli()