"""CLI entry point for pomo."""

from typing import Optional

import typer
from typing_extensions import Annotated

from pomo import __version__
from pomo.config import get_config, Config
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

    status = read_status()

    # No active session
    if status.end is None:
        return

    config = get_config()
    remaining = get_remaining(status)
    emoji = get_emoji(config, status, remaining)
    formatted = format_duration(remaining)

    typer.echo(f"{emoji} {formatted}")


@app.command()
def start(
    duration: Annotated[
        Optional[str],
        typer.Argument(help="Duration (e.g., 25m, 1h30m)"),
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
    )
    write_status(status)
    success(f"Focus session started ({format_duration(dur)})")


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
    """Stop the current session."""
    write_status(Status())
    info("Session stopped")


@app.command()
def status() -> None:
    """Show detailed status of the current session."""
    status = read_status()

    if status.end is None:
        info("No active session")
        return

    remaining = get_remaining(status)
    session_type = "Focus" if status.session_type == SessionType.FOCUS else "Break"

    info(f"Session: {session_type}")
    info(f"Remaining: {format_duration(remaining)}")


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
