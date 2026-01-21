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


@dataclass
class Status:
    """Current session status."""

    session_type: SessionType = SessionType.FOCUS
    end: Optional[datetime] = None
    notified: bool = False
    duration_seconds: int = 0

    def __post_init__(self):
        """Set end time based on duration if not already set."""
        if self.duration_seconds > 0 and self.end is None:
            self.end = datetime.now(timezone.utc).replace(microsecond=0) + \
                       __import__("datetime").timedelta(seconds=self.duration_seconds)


def get_status_path() -> Path:
    """Get the status file path."""
    return get_config_dir() / "status.json"


def write_status(status: Status) -> None:
    """Write status to file."""
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)

    data = {
        "type": int(status.session_type),
        "end": status.end.isoformat() if status.end else None,
        "notified": status.notified,
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

        end = None
        if data.get("end"):
            end = datetime.fromisoformat(data["end"])

        return Status(
            session_type=SessionType(data.get("type", 1)),
            end=end,
            notified=data.get("notified", False),
        )
    except (json.JSONDecodeError, KeyError, ValueError):
        return Status()
