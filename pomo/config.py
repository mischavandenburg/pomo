"""Configuration management for pomo."""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Durations:
    """Default durations for sessions."""

    focus: int = 25 * 60  # 25 minutes in seconds
    break_: int = 5 * 60  # 5 minutes in seconds


@dataclass
class Emojis:
    """Emojis for different states."""

    focus: str = "\U0001F345"  # Tomato
    break_: str = "\U0001F942"  # Clinking glasses
    warn: list[str] = field(default_factory=lambda: ["\U0001F534", "\U00002B55"])  # Red circle, hollow circle


@dataclass
class Config:
    """Application configuration."""

    durations: Durations = field(default_factory=Durations)
    emojis: Emojis = field(default_factory=Emojis)
    sound: str = "default"


def get_config_dir() -> Path:
    """Get the configuration directory path."""
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        return Path(xdg_config) / "pomo"
    return Path.home() / ".config" / "pomo"


def get_config_path() -> Path:
    """Get the configuration file path."""
    return get_config_dir() / "config.json"


_config: Optional[Config] = None


def get_config() -> Config:
    """Load and return the configuration."""
    global _config

    if _config is not None:
        return _config

    config = Config()
    config_path = get_config_path()

    if config_path.exists():
        try:
            with open(config_path) as f:
                data = json.load(f)

            if "durations" in data:
                if "focus" in data["durations"]:
                    config.durations.focus = parse_duration_config(data["durations"]["focus"])
                if "break" in data["durations"]:
                    config.durations.break_ = parse_duration_config(data["durations"]["break"])

            if "emojis" in data:
                if "focus" in data["emojis"]:
                    config.emojis.focus = data["emojis"]["focus"]
                if "break" in data["emojis"]:
                    config.emojis.break_ = data["emojis"]["break"]
                if "warn" in data["emojis"]:
                    config.emojis.warn = data["emojis"]["warn"]

            if "sound" in data:
                config.sound = data["sound"]

        except (json.JSONDecodeError, KeyError):
            pass  # Use defaults on error

    _config = config
    return config


def parse_duration_config(value: str | int) -> int:
    """Parse a duration from config (e.g., '25m' or 1500)."""
    if isinstance(value, int):
        return value

    import re

    total_seconds = 0
    pattern = r"(\d+)([hms])"
    matches = re.findall(pattern, value.lower())

    if not matches:
        try:
            return int(value) * 60  # Assume minutes
        except ValueError:
            return 25 * 60  # Default

    for num, unit in matches:
        if unit == "h":
            total_seconds += int(num) * 3600
        elif unit == "m":
            total_seconds += int(num) * 60
        elif unit == "s":
            total_seconds += int(num)

    return total_seconds
