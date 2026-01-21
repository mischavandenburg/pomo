"""Output formatting utilities for pomo."""

import typer


def success(message: str) -> None:
    """Print a success message."""
    typer.echo(typer.style(message, fg=typer.colors.GREEN))


def info(message: str) -> None:
    """Print an info message."""
    typer.echo(message)


def error(message: str) -> None:
    """Print an error message."""
    typer.echo(typer.style(f"Error: {message}", fg=typer.colors.RED), err=True)
