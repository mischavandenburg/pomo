"""Tests for pomo notification module."""

from unittest.mock import patch, MagicMock

from pomo.notify import (
    is_notify_available,
    get_notification_title,
    get_notification_body,
    send_notification,
)
from pomo.status import Status, SessionType


class TestNotificationTitle:
    """Test notification title generation."""

    def test_focus_title(self):
        """Focus session should have correct title."""
        title = get_notification_title(SessionType.FOCUS)
        assert title == "Focus Session Complete"

    def test_break_title(self):
        """Break session should have correct title."""
        title = get_notification_title(SessionType.BREAK)
        assert title == "Break Time Over"

    def test_deep_title(self):
        """Deep work session should have correct title."""
        title = get_notification_title(SessionType.DEEP)
        assert title == "Deep Work Session Complete"


class TestNotificationBody:
    """Test notification body generation."""

    def test_focus_body(self):
        """Focus session should have correct body."""
        body = get_notification_body(SessionType.FOCUS)
        assert body == "Focus session has ended."

    def test_break_body(self):
        """Break session should have correct body."""
        body = get_notification_body(SessionType.BREAK)
        assert body == "Break has ended."

    def test_deep_body(self):
        """Deep work session should have correct body."""
        body = get_notification_body(SessionType.DEEP)
        assert body == "Deep work session has ended."

    def test_body_with_notes(self):
        """Body should include notes when provided."""
        body = get_notification_body(SessionType.FOCUS, notes="Working on API")
        assert "Focus session has ended." in body
        assert "Working on API" in body

    def test_body_without_notes(self):
        """Body should work without notes."""
        body = get_notification_body(SessionType.FOCUS, notes=None)
        assert body == "Focus session has ended."


class TestNotifyAvailable:
    """Test notify-send availability check."""

    @patch("pomo.notify.shutil.which")
    def test_available_when_exists(self, mock_which):
        """Should return True when notify-send exists."""
        mock_which.return_value = "/usr/bin/notify-send"
        assert is_notify_available() is True
        mock_which.assert_called_once_with("notify-send")

    @patch("pomo.notify.shutil.which")
    def test_not_available_when_missing(self, mock_which):
        """Should return False when notify-send is missing."""
        mock_which.return_value = None
        assert is_notify_available() is False


class TestSendNotification:
    """Test sending notifications."""

    @patch("pomo.notify.subprocess.run")
    @patch("pomo.notify.is_notify_available")
    def test_send_notification_success(self, mock_available, mock_run):
        """Should send notification successfully."""
        mock_available.return_value = True
        mock_run.return_value = MagicMock(returncode=0)

        status = Status(
            session_type=SessionType.FOCUS,
            duration_seconds=60,
        )

        result = send_notification(status)

        assert result is True
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "notify-send" in args
        assert "--urgency" in args
        assert "normal" in args
        assert "Focus Session Complete" in args

    @patch("pomo.notify.subprocess.run")
    @patch("pomo.notify.is_notify_available")
    def test_send_notification_with_urgency(self, mock_available, mock_run):
        """Should send notification with custom urgency."""
        mock_available.return_value = True
        mock_run.return_value = MagicMock(returncode=0)

        status = Status(
            session_type=SessionType.FOCUS,
            duration_seconds=60,
        )

        send_notification(status, urgency="critical")

        args = mock_run.call_args[0][0]
        assert "critical" in args

    @patch("pomo.notify.subprocess.run")
    @patch("pomo.notify.is_notify_available")
    def test_send_notification_with_icon(self, mock_available, mock_run):
        """Should send notification with icon."""
        mock_available.return_value = True
        mock_run.return_value = MagicMock(returncode=0)

        status = Status(
            session_type=SessionType.FOCUS,
            duration_seconds=60,
        )

        send_notification(status, icon="alarm")

        args = mock_run.call_args[0][0]
        assert "--icon" in args
        assert "alarm" in args

    @patch("pomo.notify.is_notify_available")
    def test_send_notification_when_unavailable(self, mock_available):
        """Should return False when notify-send is unavailable."""
        mock_available.return_value = False

        status = Status(
            session_type=SessionType.FOCUS,
            duration_seconds=60,
        )

        result = send_notification(status)

        assert result is False

    @patch("pomo.notify.subprocess.run")
    @patch("pomo.notify.is_notify_available")
    def test_send_notification_handles_timeout(self, mock_available, mock_run):
        """Should handle timeout gracefully."""
        import subprocess

        mock_available.return_value = True
        mock_run.side_effect = subprocess.TimeoutExpired("notify-send", 5)

        status = Status(
            session_type=SessionType.FOCUS,
            duration_seconds=60,
        )

        result = send_notification(status)

        assert result is False

    @patch("pomo.notify.subprocess.run")
    @patch("pomo.notify.is_notify_available")
    def test_send_notification_handles_error(self, mock_available, mock_run):
        """Should handle subprocess error gracefully."""
        import subprocess

        mock_available.return_value = True
        mock_run.side_effect = subprocess.CalledProcessError(1, "notify-send")

        status = Status(
            session_type=SessionType.FOCUS,
            duration_seconds=60,
        )

        result = send_notification(status)

        assert result is False

    @patch("pomo.notify.subprocess.run")
    @patch("pomo.notify.is_notify_available")
    def test_send_notification_includes_notes(self, mock_available, mock_run):
        """Should include notes in notification body."""
        mock_available.return_value = True
        mock_run.return_value = MagicMock(returncode=0)

        status = Status(
            session_type=SessionType.FOCUS,
            duration_seconds=60,
            notes="Working on API refactor",
        )

        send_notification(status)

        args = mock_run.call_args[0][0]
        body = args[-1]  # Last argument is the body
        assert "Working on API refactor" in body
