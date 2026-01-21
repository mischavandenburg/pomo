"""CLI entry point for pomo."""

from datetime import datetime, timezone
from typing import Optional

import typer
from typing_extensions import Annotated

from pomo import __version__
from pomo.config import get_config
from pomo.db import init_db, sync_session, get_sessions
from pomo.notify import send_notification
from pomo.status import read_status, write_status, Status, SessionType
from pomo.output import success, info, error
from pomo.timer import get_remaining, format_duration, get_emoji

app = typer.Typer(
    name="pomo",
    help="A pomodoro timer CLI with quantified-self tracking.",
    no_args_is_help=False,
)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """
    Show the current pomodoro status.

    If no command is provided, displays the remaining time of the active session.
    """
    if ctx.invoked_subcommand is not None:
        return

    current_status = read_status()

    # No active session
    if current_status.end is None:
        return

    config = get_config()
    remaining = get_remaining(current_status)
    emoji = get_emoji(config, current_status, remaining)
    formatted = format_duration(remaining)

    # Clean output only - just emoji + time for tmux
    typer.echo(f"{emoji} {formatted}")

    # Silent auto-sync when timer completes
    if remaining <= 0 and not current_status.notified and current_status.start:
        # Send desktop notification
        if config.notifications.enabled:
            send_notification(
                current_status,
                urgency=config.notifications.urgency,
                icon=config.notifications.icon,
            )

        sync_session(
            session_type=current_status.session_type.name.lower(),
            started_at=current_status.start,
            ended_at=current_status.end,
            planned_seconds=current_status.duration_seconds,
            completed=True,
            notes=current_status.notes,
        )
        current_status.notified = True
        write_status(current_status)


@app.command()
def start(
    notes: Annotated[
        Optional[str],
        typer.Argument(help="What you're working on"),
    ] = None,
    duration: Annotated[
        Optional[str],
        typer.Option("--duration", "-d", help="Duration (e.g., 25m, 1h30m)"),
    ] = None,
) -> None:
    """
    Start a focus session.

    Uses the default focus duration from config if not specified.
    """
    config = get_config()
    dur = parse_duration(duration) if duration else config.durations.focus

    status = Status(
        session_type=SessionType.FOCUS,
        duration_seconds=dur,
        notes=notes,
    )
    write_status(status)
    msg = f"Focus session started ({format_duration(dur)})"
    if notes:
        msg += f' - "{notes}"'
    success(msg)


@app.command()
def deep(
    notes: Annotated[
        Optional[str],
        typer.Argument(help="What you're working on"),
    ] = None,
    duration: Annotated[
        Optional[str],
        typer.Option("--duration", "-d", help="Duration (e.g., 90m, 2h)"),
    ] = None,
) -> None:
    """
    Start a deep work session (90 minutes default).

    Deep work sessions are longer, focused periods for complex tasks.
    """
    config = get_config()
    dur = parse_duration(duration) if duration else config.durations.deep

    status = Status(
        session_type=SessionType.DEEP,
        duration_seconds=dur,
        notes=notes,
    )
    write_status(status)
    msg = f"Deep work started ({format_duration(dur)})"
    if notes:
        msg += f' - "{notes}"'
    success(msg)


@app.command(name="break")
def break_cmd(
    duration: Annotated[
        Optional[str],
        typer.Argument(help="Duration (e.g., 5m, 10m)"),
    ] = None,
) -> None:
    """
    Start a break.

    Uses the default break duration from config if not specified.
    """
    config = get_config()
    dur = parse_duration(duration) if duration else config.durations.break_

    status = Status(
        session_type=SessionType.BREAK,
        duration_seconds=dur,
    )
    write_status(status)
    success(f"Break started ({format_duration(dur)})")


@app.command()
def stop() -> None:
    """Stop the current session early."""
    current_status = read_status()

    # Sync to database if there was an active session
    if current_status.start and not current_status.notified:
        ended_at = datetime.now(timezone.utc)
        synced = sync_session(
            session_type=current_status.session_type.name.lower(),
            started_at=current_status.start,
            ended_at=ended_at,
            planned_seconds=current_status.duration_seconds,
            completed=False,  # Stopped early
            notes=current_status.notes,
        )
        if synced:
            info("Session synced to database (stopped early)")

    write_status(Status())
    info("Session stopped")


@app.command()
def status() -> None:
    """Show detailed status of the current session."""
    current_status = read_status()

    if current_status.end is None:
        info("No active session")
        return

    remaining = get_remaining(current_status)
    session_type = current_status.session_type.name.capitalize()

    info(f"Session: {session_type}")
    info(f"Remaining: {format_duration(remaining)}")
    if current_status.notes:
        info(f"Notes: {current_status.notes}")
    if current_status.start:
        info(f"Started: {current_status.start.strftime('%H:%M')}")


@app.command()
def init() -> None:
    """Initialize database table for session tracking."""
    if init_db():
        success("Database initialized successfully")
    else:
        error("Failed to initialize database. Check POMO_DATABASE_URL.")
        raise typer.Exit(code=1)


@app.command(name="list")
def list_sessions(
    limit: Annotated[
        int,
        typer.Argument(help="Number of sessions to show"),
    ] = 10,
) -> None:
    """List recent sessions from the database."""
    sessions = get_sessions(limit)

    if not sessions:
        info("No sessions found (check POMO_DATABASE_URL)")
        return

    for session in sessions:
        session_type = session["session_type"].capitalize()
        started = session["started_at"].strftime("%Y-%m-%d %H:%M")
        completed = "+" if session["completed"] else "-"
        duration = format_duration(session["actual_seconds"] or session["planned_seconds"])
        notes = session["notes"] or ""

        if notes:
            typer.echo(f"{completed} {started}  {session_type:5}  {duration:>7}  {notes}")
        else:
            typer.echo(f"{completed} {started}  {session_type:5}  {duration:>7}")


@app.command()
def version() -> None:
    """Show the version."""
    typer.echo(f"pomo {__version__}")


def parse_duration(duration_str: str) -> int:
    """Parse a duration string like '25m' or '1h30m' into seconds."""
    import re

    total_seconds = 0
    pattern = r"(\d+)([hms])"
    matches = re.findall(pattern, duration_str.lower())

    if not matches:
        # Try parsing as just minutes
        try:
            return int(duration_str) * 60
        except ValueError:
            error(f"Invalid duration format: {duration_str}")
            raise typer.Exit(code=1)

    for value, unit in matches:
        if unit == "h":
            total_seconds += int(value) * 3600
        elif unit == "m":
            total_seconds += int(value) * 60
        elif unit == "s":
            total_seconds += int(value)

    return total_seconds


if __name__ == "__main__":
    app()
