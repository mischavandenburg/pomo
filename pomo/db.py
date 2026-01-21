"""Database operations for pomo session tracking."""

import os
from datetime import datetime
from typing import Optional

import psycopg


def get_connection() -> Optional[psycopg.Connection]:
    """Get DB connection from POMO_DATABASE_URL env var."""
    url = os.getenv("POMO_DATABASE_URL")
    if not url:
        return None
    try:
        return psycopg.connect(url)
    except psycopg.Error:
        return None


def init_db() -> bool:
    """Create the pomodoro_sessions table."""
    conn = get_connection()
    if not conn:
        return False

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS pomodoro_sessions (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        session_type VARCHAR(10) NOT NULL,
                        started_at TIMESTAMPTZ NOT NULL,
                        ended_at TIMESTAMPTZ,
                        planned_duration_seconds INT NOT NULL,
                        actual_duration_seconds INT,
                        completed BOOLEAN DEFAULT FALSE,
                        notes TEXT,
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    )
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_pomo_sessions_started_at
                    ON pomodoro_sessions(started_at)
                """)
        return True
    except psycopg.Error:
        return False
    finally:
        conn.close()


def get_sessions(limit: int = 10) -> list[dict]:
    """Fetch recent sessions from the database."""
    conn = get_connection()
    if not conn:
        return []

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT session_type, started_at, ended_at,
                           planned_duration_seconds, actual_duration_seconds,
                           completed, notes
                    FROM pomodoro_sessions
                    ORDER BY started_at DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                rows = cur.fetchall()
                return [
                    {
                        "session_type": row[0],
                        "started_at": row[1],
                        "ended_at": row[2],
                        "planned_seconds": row[3],
                        "actual_seconds": row[4],
                        "completed": row[5],
                        "notes": row[6],
                    }
                    for row in rows
                ]
    except psycopg.Error:
        return []
    finally:
        conn.close()


def sync_session(
    session_type: str,
    started_at: datetime,
    ended_at: Optional[datetime],
    planned_seconds: int,
    completed: bool,
    notes: Optional[str] = None,
) -> bool:
    """Sync a completed session to the database."""
    conn = get_connection()
    if not conn:
        return False

    actual_seconds = None
    if ended_at:
        actual_seconds = int((ended_at - started_at).total_seconds())

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO pomodoro_sessions
                    (session_type, started_at, ended_at, planned_duration_seconds,
                     actual_duration_seconds, completed, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        session_type,
                        started_at,
                        ended_at,
                        planned_seconds,
                        actual_seconds,
                        completed,
                        notes,
                    ),
                )
        return True
    except psycopg.Error:
        return False
    finally:
        conn.close()
