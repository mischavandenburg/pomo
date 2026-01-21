"""Desktop notification support for pomo."""

import shutil
import subprocess
from typing import Optional

from pomo.status import Status, SessionType


def is_notify_available() -> bool:
    """Check if notify-send is available on the system."""
    return shutil.which("notify-send") is not None


def get_notification_title(session_type: SessionType) -> str:
    """Get the notification title based on session type."""
    titles = {
        SessionType.FOCUS: "Focus Session Complete",
        SessionType.BREAK: "Break Time Over",
        SessionType.DEEP: "Deep Work Session Complete",
    }
    return titles.get(session_type, "Timer Complete")


def get_notification_body(session_type: SessionType, notes: Optional[str] = None) -> str:
    """Get the notification body based on session type and notes."""
    bodies = {
        SessionType.FOCUS: "Focus session has ended.",
        SessionType.BREAK: "Break has ended.",
        SessionType.DEEP: "Deep work session has ended.",
    }
    body = bodies.get(session_type, "Timer has ended.")

    if notes:
        body += f"\n\n{notes}"

    return body


def send_notification(
    status: Status,
    urgency: str = "normal",
    icon: Optional[str] = None,
) -> bool:
    """
    Send a desktop notification using notify-send.

    Args:
        status: The current session status
        urgency: Notification urgency (low, normal, critical)
        icon: Optional icon name for the notification

    Returns:
        True if notification was sent successfully, False otherwise
    """
    if not is_notify_available():
        return False

    title = get_notification_title(status.session_type)
    body = get_notification_body(status.session_type, status.notes)

    cmd = [
        "notify-send",
        "--urgency", urgency,
    ]

    if icon:
        cmd.extend(["--icon", icon])

    cmd.extend([title, body])

    try:
        subprocess.run(cmd, check=True, timeout=5)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False
