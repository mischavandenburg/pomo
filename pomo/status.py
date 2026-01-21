"""Session status management for pomo."""

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import IntEnum
from pathlib import Path
from typing import Optional

from pomo.config import get_config_dir


class SessionType(IntEnum):
    """Type of pomodoro session."""

    BREAK = 0
    FOCUS = 1
    DEEP = 2


@dataclass
class Status:
    """Current session status."""

    session_type: SessionType = SessionType.FOCUS
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    notified: bool = False
    duration_seconds: int = 0
    notes: Optional[str] = None

    def __post_init__(self):
        """Set start and end time based on duration if not already set."""
        if self.duration_seconds > 0:
            now = datetime.now(timezone.utc).replace(microsecond=0)
            if self.start is None:
                self.start = now
            if self.end is None:
                self.end = now + __import__("datetime").timedelta(seconds=self.duration_seconds)


def get_status_path() -> Path:
    """Get the status file path."""
    return get_config_dir() / "status.json"


def write_status(status: Status) -> None:
    """Write status to file."""
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)

    data = {
        "type": int(status.session_type),
        "start": status.start.isoformat() if status.start else None,
        "end": status.end.isoformat() if status.end else None,
        "notified": status.notified,
        "duration_seconds": status.duration_seconds,
        "notes": status.notes,
    }

    with open(get_status_path(), "w") as f:
        json.dump(data, f)


def read_status() -> Status:
    """Read status from file."""
    status_path = get_status_path()

    if not status_path.exists():
        return Status()

    try:
        with open(status_path) as f:
            data = json.load(f)

        start = None
        if data.get("start"):
            start = datetime.fromisoformat(data["start"])

        end = None
        if data.get("end"):
            end = datetime.fromisoformat(data["end"])

        return Status(
            session_type=SessionType(data.get("type", 1)),
            start=start,
            end=end,
            notified=data.get("notified", False),
            duration_seconds=data.get("duration_seconds", 0),
            notes=data.get("notes"),
        )
    except (json.JSONDecodeError, KeyError, ValueError):
        return Status()
