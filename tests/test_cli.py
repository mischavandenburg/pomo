"""Tests for pomo CLI."""


from typer.testing import CliRunner

from pomo import __version__
from pomo.main import app, parse_duration
from pomo.timer import format_duration
from pomo.status import Status, SessionType


runner = CliRunner()


class TestVersion:
    """Test version."""

    def test_version_is_semver(self):
        """Version should be semantic versioning format."""
        parts = __version__.split(".")
        assert len(parts) == 3
        assert all(part.isdigit() for part in parts)

    def test_version_command(self):
        """Version command should show version."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert __version__ in result.stdout


class TestCLI:
    """Test CLI commands."""

    def test_help_shows_commands(self):
        """Help should list available commands."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "start" in result.stdout
        assert "break" in result.stdout
        assert "stop" in result.stdout
        assert "status" in result.stdout

    def test_start_help(self):
        """Start command should have help text."""
        result = runner.invoke(app, ["start", "--help"])
        assert result.exit_code == 0
        assert "focus" in result.stdout.lower()

    def test_break_help(self):
        """Break command should have help text."""
        result = runner.invoke(app, ["break", "--help"])
        assert result.exit_code == 0
        assert "break" in result.stdout.lower()

    def test_stop_help(self):
        """Stop command should have help text."""
        result = runner.invoke(app, ["stop", "--help"])
        assert result.exit_code == 0
        assert "Stop" in result.stdout


class TestParseDuration:
    """Test duration parsing."""

    def test_parse_minutes(self):
        """Should parse minutes."""
        assert parse_duration("25m") == 25 * 60
        assert parse_duration("5m") == 5 * 60

    def test_parse_hours(self):
        """Should parse hours."""
        assert parse_duration("1h") == 3600
        assert parse_duration("2h") == 7200

    def test_parse_combined(self):
        """Should parse combined durations."""
        assert parse_duration("1h30m") == 5400
        assert parse_duration("1h30m30s") == 5430

    def test_parse_plain_number(self):
        """Should treat plain numbers as minutes."""
        assert parse_duration("25") == 25 * 60


class TestFormatDuration:
    """Test duration formatting."""

    def test_format_seconds(self):
        """Should format seconds."""
        assert format_duration(30) == "30s"
        assert format_duration(59) == "59s"

    def test_format_minutes(self):
        """Should format minutes and seconds."""
        assert format_duration(60) == "1m00s"
        assert format_duration(90) == "1m30s"
        assert format_duration(25 * 60) == "25m00s"

    def test_format_hours(self):
        """Should format hours and minutes."""
        assert format_duration(3600) == "1h00m"
        assert format_duration(3660) == "1h01m"
        assert format_duration(5400) == "1h30m"

    def test_format_negative(self):
        """Should format negative durations."""
        assert format_duration(-60) == "-1m00s"
        assert format_duration(-30) == "-30s"


class TestStatus:
    """Test Status model."""

    def test_default_status(self):
        """Default status should have no end time."""
        status = Status()
        assert status.end is None
        assert status.session_type == SessionType.FOCUS
        assert status.notified is False

    def test_status_with_duration(self):
        """Status with duration should set end time."""
        status = Status(duration_seconds=60)
        assert status.end is not None

    def test_session_types(self):
        """Session types should be correct values."""
        assert SessionType.BREAK == 0
        assert SessionType.FOCUS == 1
