# modules/acc_managt/delete_acc.py
from pathlib import Path
from database.db import delete_account, get_account, verify_password
from modules.utilities.error_handler import get_error_logger
from modules.utilities.logger import get_logger
logger = get_logger(__name__)
errorLogger = get_error_logger(__name__)

def delete_account_cli(root: Path):
    username = input("Enter username to delete: ").strip()
    acc = get_account(username)
    if not acc:
        print("User not found")
        logger.info(f"{username} not found ")
        return
    password = input("Enter your password to confirm deletion: ").strip()
    if not verify_password(username, password):
        print("Incorrect password")
        logger.info("Incorrect passwsord")
        return
    ok = delete_account(username)
    if ok:
        print(f"Deleted account: {username}")
        logger.info(f"Deleted account: {username}")
    else:
        print("Failed to delete account")
        errorLogger.exception(f"Failed to delete {username} account")
    return ok

if __name__ == "__main__":
    delete_account_cli()