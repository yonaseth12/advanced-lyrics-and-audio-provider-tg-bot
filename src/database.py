import aiosqlite
import logging
import os
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_PATH", "data/bot.db")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    telegram_user_id INTEGER PRIMARY KEY,
    username         TEXT,
    first_name       TEXT,
    last_name        TEXT,
    first_seen       TEXT NOT NULL,
    last_seen        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS search_history (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id INTEGER NOT NULL,
    query            TEXT NOT NULL,
    result_count     INTEGER,
    status           TEXT NOT NULL,  -- 'success', 'no_results', 'error'
    error_type       TEXT,
    created_at       TEXT NOT NULL,
    FOREIGN KEY (telegram_user_id) REFERENCES users(telegram_user_id)
);

CREATE INDEX IF NOT EXISTS idx_search_user ON search_history(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_search_date ON search_history(created_at);
"""


async def init_db():
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(_SCHEMA)
        await db.commit()
    logger.info("Database initialised at %s", DB_PATH)


async def upsert_user(user) -> None:
    """Insert or update a Telegram user record."""
    now = datetime.now(timezone.utc).isoformat()
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                """
                INSERT INTO users (telegram_user_id, username, first_name, last_name, first_seen, last_seen)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(telegram_user_id) DO UPDATE SET
                    username   = excluded.username,
                    first_name = excluded.first_name,
                    last_name  = excluded.last_name,
                    last_seen  = excluded.last_seen
                """,
                (user.id, user.username, user.first_name, user.last_name, now, now),
            )
            await db.commit()
    except Exception:
        logger.exception("Failed to upsert user %s", user.id)


async def log_search(telegram_user_id: int, query: str, result_count: int | None,
                     status: str, error_type: str | None = None) -> None:
    now = datetime.now(timezone.utc).isoformat()
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                """
                INSERT INTO search_history (telegram_user_id, query, result_count, status, error_type, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (telegram_user_id, query, result_count, status, error_type, now),
            )
            await db.commit()
    except Exception:
        logger.exception("Failed to log search for user %s", telegram_user_id)
