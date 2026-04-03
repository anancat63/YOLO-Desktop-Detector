from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Generator, List, Optional, Tuple

from . import config as Config

UserRow = Tuple[int, str, str]


def _placeholder() -> str:
    return "?" if Config.get_db_engine() == "sqlite" else "%s"


def _create_users_table_sql() -> str:
    if Config.get_db_engine() == "sqlite":
        return (
            """
            CREATE TABLE IF NOT EXISTS user_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
            """
        )

    return (
        """
        CREATE TABLE IF NOT EXISTS user_accounts (
            id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(128) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )


@contextmanager
def db_connection() -> Generator:
    engine = Config.get_db_engine()

    if engine == "sqlite":
        import os

        db_path = Config.get_sqlite_path()
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return

    if engine == "mysql":
        try:
            import pymysql
        except ModuleNotFoundError as exc:
            raise RuntimeError("MySQL mode requires pymysql. Install with: pip install pymysql") from exc

        conn = pymysql.connect(**Config.get_mysql_config())
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return

    raise ValueError(f"Unsupported database engine: {engine}")


def init_database() -> Optional[str]:
    with db_connection() as conn:
        cur = conn.cursor()
        cur.execute(_create_users_table_sql())

        ph = _placeholder()
        cur.execute(f"SELECT COUNT(1) FROM user_accounts WHERE username={ph}", ("admin",))
        exists = cur.fetchone()[0]
        if int(exists) == 0:
            cur.execute(
                f"INSERT INTO user_accounts (username, password) VALUES ({ph}, {ph})",
                ("admin", "admin123"),
            )

    if Config.get_db_engine() == "mysql":
        return "MySQL connected successfully. Make sure credentials in app_config.json are correct."

    return None


def get_user_by_username(username: str) -> Optional[UserRow]:
    ph = _placeholder()
    with db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"SELECT id, username, password FROM user_accounts WHERE username={ph}",
            (username,),
        )
        row = cur.fetchone()

    if not row:
        return None
    return int(row[0]), str(row[1]), str(row[2])


def create_user(username: str, password: str) -> bool:
    if get_user_by_username(username):
        return False

    ph = _placeholder()
    with db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"INSERT INTO user_accounts (username, password) VALUES ({ph}, {ph})",
            (username, password),
        )
    return True


def authenticate_user(username: str, password: str) -> bool:
    user = get_user_by_username(username)
    return bool(user and user[2] == password)


def fetch_users() -> List[UserRow]:
    with db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, username, password FROM user_accounts ORDER BY id ASC")
        rows = cur.fetchall()

    return [(int(r[0]), str(r[1]), str(r[2])) for r in rows]


def update_user(user_id: int, username: str, password: str) -> None:
    ph = _placeholder()
    with db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"UPDATE user_accounts SET username={ph}, password={ph} WHERE id={ph}",
            (username, password, user_id),
        )


def delete_user(user_id: int) -> None:
    ph = _placeholder()
    with db_connection() as conn:
        cur = conn.cursor()
        cur.execute(f"DELETE FROM user_accounts WHERE id={ph}", (user_id,))
