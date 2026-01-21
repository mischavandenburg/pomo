"""Timer utilities for pomo."""

from datetime import datetime, timezone

from pomo.config import Config
from pomo.status import Status, SessionType


def get_remaining(status: Status) -> int:
    """Get remaining seconds in the current session."""
    if status.end is None:
        return 0

    now = datetime.now(timezone.utc)
    remaining = (status.end - now).total_seconds()
    return int(remaining)


def format_duration(seconds: int) -> str:
    """Format seconds as a human-readable duration."""
    negative = seconds < 0
    seconds = abs(seconds)

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    sign = "-" if negative else ""

    if hours >= 1:
        return f"{sign}{hours}h{minutes:02d}m"
    elif minutes >= 1:
        return f"{sign}{minutes}m{secs:02d}s"
    else:
        return f"{sign}{secs}s"


def get_emoji(config: Config, status: Status, remaining: int) -> str:
    """Get the appropriate emoji for the current state."""
    # Blink warning emoji when time is up
    if remaining <= 0:
        index = abs(remaining) % len(config.emojis.warn)
        return config.emojis.warn[index]

    if status.session_type == SessionType.FOCUS:
        return config.emojis.focus
    elif status.session_type == SessionType.DEEP:
        return config.emojis.deep
    else:
        return config.emojis.break_
