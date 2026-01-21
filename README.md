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

Prints the status of the current session. Clean output for tmux statusline.

```bash
pomo
# 🍅 23m45s
```

### Start focus

Starts a new pomodoro focus session with the default duration (25 minutes).

```bash
pomo start
pomo start "Working on feature"
pomo start "Quick fix" -d 15m
```

### Deep work

Starts a deep work session (90 minutes default) for extended focus periods.

```bash
pomo deep
pomo deep "Writing blog post"
pomo deep "API refactor" -d 2h
```

### Start break

Starts a new break with the default duration (5 minutes).

```bash
pomo break
pomo break 10m
```

### Stop session

Stops the current pomodoro session. If database is configured, syncs as incomplete.

```bash
pomo stop
```

### Show detailed status

Shows detailed information about the current session including notes and start time.

```bash
pomo status
# Session: Deep
# Remaining: 1h23m
# Notes: Writing blog post
# Started: 14:30
```

## Database Integration (Optional)

Pomo can sync sessions to a PostgreSQL database for quantified-self tracking. This is entirely optional - pomo works fully offline without any database configuration.

### Setup

1. Set the database URL:

```bash
export POMO_DATABASE_URL="postgresql://user:password@host/database"
```

2. Initialize the database table:

```bash
pomo init
```

### Behavior

When `POMO_DATABASE_URL` is set:
- Sessions are automatically synced when the timer completes
- Early stops are synced with `completed=false`
- All syncing happens silently in the background

### Schema

```sql
CREATE TABLE pomodoro_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_type VARCHAR(10) NOT NULL,  -- 'focus', 'deep', 'break'
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    planned_duration_seconds INT NOT NULL,
    actual_duration_seconds INT,
    completed BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Configuration

The default values can be customized by creating a `~/.config/pomo/config.json` file:

```json
{
  "durations": {
    "focus": "25m",
    "break": "5m",
    "deep": "90m"
  },
  "emojis": {
    "focus": "🍅",
    "break": "🥂",
    "deep": "🍅",
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
