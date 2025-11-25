# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

tmux-iterm-command is a command-line tool that bridges coding agents (Claude, Qwen, Gemini, Codex) with tmux. It enables coding agents to programmatically:
- Create and manage tmux windows and panes within existing sessions
- Execute commands and capture output
- Interact with terminal sessions in a structured way
- Operate within existing tmux sessions (does not create/destroy entire sessions)

## Project Architecture

### Core Components

1. **CLI Entry Point** (`src/claude_tmux/cli.py`)
   - Argument parsing using Click framework
   - Command routing and delegation
   - Main interface for external callers (coding agents)

2. **Tmux Abstraction Layer** (`src/claude_tmux/manager.py`)
   - Uses libtmux library for tmux operations (no subprocess calls)
   - Session detection and management within existing sessions
   - Window and pane operations
   - Command execution and output capture

3. **Command Handlers** (`src/claude_tmux/commands.py`)
   - Individual command modules for each CLI command
   - Each follows Click command pattern
   - Encapsulates command logic and option parsing

### Data Flow

User (Claude Code Agent) → CLI Arguments → Command Router → Handler → Tmux Binary/iTerm2 API → Terminal Session

## Development Setup

### Initial Setup

```bash
# Install Python dependencies
pip install -e .

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### Running the Tool

```bash
# Show available commands
tmux-iterm-command --help

# Run a specific command with options
tmux-iterm-command create-window --name editor

# For development: run directly with Python
python -m src.tmux_iterm_command.cli <command> <args>
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_tmux_manager.py

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_tmux_manager.py::test_create_window
```

## Common Commands

### Tmux Management

```bash
# Create a window in the current/default session
tmux-iterm-command create-window --name editor --command "vim myfile.txt"

# Create a pane by splitting a window
tmux-iterm-command create-pane --window 0 --vertical --command "tail -f logs/app.log"

# List active sessions
tmux-iterm-command list-sessions

# List windows in current session
tmux-iterm-command list-windows

# List panes in a window
tmux-iterm-command list-panes --window 0
```

### Command Execution

```bash
# Send a command to a specific pane
tmux-iterm-command send-command --window 0 --pane 0 "npm install"

# Send command without pressing Enter
tmux-iterm-command send-command --window 0 --pane 0 --no-enter "echo hello"

# Capture pane output
tmux-iterm-command capture-pane --window 0 --pane 0 --lines 100

# Wait for pane to be idle (no output for 2 seconds, timeout after 30s)
tmux-iterm-command wait-idle --window 0 --pane 0 --quiet-for 2 --timeout 30
```

### Window/Pane Management

```bash
# Kill a window
tmux-iterm-command kill-window --window 1

# Kill a pane
tmux-iterm-command kill-pane --window 0 --pane 1

# Detect environment capabilities
tmux-iterm-command detect

# Show current status
tmux-iterm-command status
```

## Key Architecture Patterns

### Tmux libtmux Pattern

All tmux interactions use the libtmux library, which provides a Pythonic interface to tmux. This ensures:
- Clean object-oriented API for tmux operations
- Better integration with Python error handling
- Consistent behavior across different environments

```python
# Pattern: Use libtmux Server, Session, Window, and Pane objects
from libtmux import Server
server = Server()
session = server.sessions[0]  # Get first session
window = session.new_window(window_name="my_window")
```

### Command Handler Interface

Each command handler follows this pattern:

```python
# src/claude_tmux/commands.py
import click

@click.command()
@click.option('--window', 'window_index', type=int, required=True, help='Window index')
@click.option('--pane', 'pane_index', type=int, required=True, help='Pane index')
def my_command(window_index, pane_index):
    """Do something in tmux."""
    # Implementation
    pass
```

### Error Handling

All commands return structured output:
- Success: `{"status": "success", ...}`
- Error: `{"status": "error", "message": "...", "code": "..."}`
- Output goes to stdout as JSON; coding agents parse responses

### Session Management Approach

The tool works within existing tmux sessions:
1. **Inside tmux**: Uses the current session
2. **Outside tmux**: Creates or attaches to a default session ('claude-dev')
3. **No session lifecycle**: Does not create/destroy entire sessions, only manages windows/panes

## Adding New Commands

1. Add function to `src/tmux_iterm_command/commands.py` (all commands are in one file currently)
2. Implement Click command with proper options
3. Add to command registration in `src/tmux_iterm_command/cli.py`
4. Write tests in `tests/test_commands.py`
5. Test manually: `tmux-iterm-command your-command --help`

## Testing Strategy

- Unit tests for tmux wrapper functions (mock libtmux calls)
- Integration tests for actual tmux operations (in isolated test sessions)
- Use pytest fixtures for session/window/pane setup and teardown
- Tests validate JSON output format for coding agent consumption

## Debugging

### Enable verbose logging

```bash
# All commands support --verbose flag
tmux-iterm-command create-window --name editor --verbose

# Or set environment variable
TMUX_ITERM_COMMAND_DEBUG=1 tmux-iterm-command create-window --name editor
```

### Check tmux status

```bash
# Inspect sessions created by the tool
tmux list-sessions
tmux list-windows -t session-name
tmux list-panes -t session-name:window-index

# Attach to a session for inspection
tmux attach-session -t session-name
```

### Common Issues

- **"Tmux not found"**: Ensure tmux is installed (`brew install tmux`)
- **Permission denied**: Check tmux socket permissions in `/tmp`
- **Command hangs**: Use appropriate timeout settings
- **Session detection**: Tool works inside or outside tmux, using appropriate session

## Dependencies

- Python 3.8+
- tmux (CLI binary for libtmux to interface with)
- libtmux: Python library for tmux control
- click: CLI framework

Core Python packages:
- `libtmux`: Tmux control library
- `click`: CLI framework
- `pytest`: Testing framework

See `requirements.txt` for full list and versions.
