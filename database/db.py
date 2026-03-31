import sqlite3
from pathlib import Path
import os
import hashlib
from typing import Optional, Dict, Any
import platform
import json
from argon2 import PasswordHasher, exceptions as argon2_exceptions

OS_TYPE = platform.system().lower()

# -------------------------
# Database paths
# -------------------------
if OS_TYPE == "windows":
    USERDIR = os.getlogin()
    LOCAL_APPDATA = f"C:\\Users\\{USERDIR}\\Desktop"
    APP_DIR = Path(LOCAL_APPDATA) / "SnortAMV"
    APP_DIR.mkdir(parents=True, exist_ok=True)
    DB_PATH = APP_DIR / "sqlite.db"
elif OS_TYPE == "linux":
    DB_PATH = Path(os.getcwd()) / "sqlite.db"
else:
    raise RuntimeError(f"Unsupported OS: {OS_TYPE}")


# -------------------------
# SQLite connection
# -------------------------
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # allows dict-like access
    return conn


# -------------------------
# Password hashing
# -------------------------
ph = PasswordHasher()


def hash_password(plaintext: str) -> str:
    """
    Hash a plaintext password using Argon2.
    """
    return ph.hash(plaintext)


def verify_password_hash(stored_hash: str, plaintext: str) -> bool:
    """
    Verify a plaintext password against an Argon2 hash.
    """
    try:
        return ph.verify(stored_hash, plaintext)
    except (argon2_exceptions.VerifyMismatchError, argon2_exceptions.InvalidHash):
        return False


# -------------------------
# Initialize DB
# -------------------------
def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            fullname TEXT,
            password TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );
        """
    )
    conn.commit()
    conn.close()


# -------------------------
# Account CRUD operations
# -------------------------
def create_account(username: str, fullname: str, password: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO accounts (username, fullname, password) VALUES (?, ?, ?)",
            (username, fullname, hash_password(password)),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_account(username: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, username, fullname, created_at FROM accounts WHERE username = ?",
        (username,),
    )
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def verify_password(username: str, password: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT password FROM accounts WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return False
    return verify_password_hash(row["password"], password)


def update_account(
    username: str,
    new_fullname: Optional[str] = None,
    new_password: Optional[str] = None,
) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    # ensure user exists
    cur.execute("SELECT id FROM accounts WHERE username = ?", (username,))
    if not cur.fetchone():
        conn.close()
        return False
    if new_fullname and new_password:
        cur.execute(
            "UPDATE accounts SET fullname = ?, password = ? WHERE username = ?",
            (new_fullname, hash_password(new_password), username),
        )
    elif new_fullname:
        cur.execute(
            "UPDATE accounts SET fullname = ? WHERE username = ?",
            (new_fullname, username),
        )
    elif new_password:
        cur.execute(
            "UPDATE accounts SET password = ? WHERE username = ?",
            (hash_password(new_password), username),
        )
    else:
        conn.close()
        return False
    conn.commit()
    conn.close()
    return True


def delete_account(username: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM accounts WHERE username = ?", (username,))
    changed = cur.rowcount
    conn.commit()
    conn.close()
    return changed > 0


def list_accounts() -> list:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, fullname, created_at FROM accounts ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# -------------------------
# Migrate from JSON
# -------------------------
def migrate_from_json(project_root: Path) -> int:
    json_path = project_root / "accounts.json"
    if not json_path.exists():
        return 0

    count = 0
    with json_path.open() as f:
        data = json.load(f)

    for username, info in data.items():
        fullname = info.get("Fullname") or info.get("fullname") or ""
        password = info.get("Password") or info.get("password") or ""
        if not username or not password:
            continue
        if create_account(username, fullname, password):
            count += 1

    # Rename migrated file
    try:
        json_path.rename(project_root / "accounts.json.migrated")
    except Exception:
        pass
    return count


# -------------------------
# Initialize DB on import
# -------------------------
init_db()
