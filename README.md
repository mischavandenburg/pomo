# Pomo

A pomodoro timer CLI with quantified-self tracking.

## Installation

```bash
# Using pipx (recommended)
pipx install git+https://github.com/mischavandenburg/pomo.git

# Using uv
uv tool install git+https://github.com/mischavandenburg/pomo.git
```

## Usage

### Show status

Prints the status of the current session.

```bash
pomo
```

### Start focus

Starts a new pomodoro focus session with the default duration (25 minutes).

```bash
pomo start
```

Or customize the session duration:

```bash
pomo start 15m
pomo start 1h30m
```

### Start break

Starts a new break with the default duration (5 minutes).

```bash
pomo break
```

Or customize the break duration:

```bash
pomo break 10m
```

### Stop session

Stops the current pomodoro session.

```bash
pomo stop
```

### Show detailed status

Shows detailed information about the current session.

```bash
pomo status
```

## Configuration

The default values can be customized by creating a `~/.config/pomo/config.json` file:

```json
{
  "durations": {
    "break": "5m",
    "focus": "25m"
  },
  "emojis": {
    "break": "🥂",
    "focus": "🍅",
    "warn": ["🔴", "⭕"]
  },
  "sound": "default"
}
```

## Development

```bash
# Clone the repository
git clone https://github.com/mischavandenburg/pomo.git
cd pomo

# Install dependencies
uv sync

# Run tests
uv run pytest

# Run linter
uv run ruff check .
```

## License

MIT
