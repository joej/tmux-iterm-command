# tmux-iterm-command - Tmux Command Tool

`tmux-iterm-command` is a command-line tool designed for coding agents (Claude, Qwen, Gemini, Codex) to manage tmux **windows and panes** within existing sessions. It provides a structured interface for coding agents to create terminal environments, run commands, capture output, and manage terminal windows/panes programmatically.

## ⚠️ CRITICAL: WINDOWS AND PANES ONLY - NEVER MANAGE SESSIONS

**For Coding Agents: DO NOT create, destroy, or manage tmux SESSIONS.**

This tool only manages **windows and panes** within existing sessions. The tool automatically handles all session management for you. If you find yourself trying to create or destroy sessions, STOP and use the tool correctly.

**What you CAN do:**
- ✅ Create/destroy windows
- ✅ Create/destroy panes (split windows)
- ✅ Send commands to panes
- ✅ Capture output

**What you CANNOT do:**
- ❌ Create tmux sessions
- ❌ Destroy tmux sessions
- ❌ Modify session configuration
- ❌ Manage session lifecycle in any way

## Features

- **Window/Pane Management**: Create, list, and destroy windows and panes (within existing sessions only)
- **Command Execution**: Send commands to specific panes and capture output
- **Session Awareness**: Works both inside and outside tmux sessions (handles session detection automatically)
- **JSON Output**: Structured responses suitable for parsing by coding agents
- **Wait Operations**: Wait for command completion or idle state

## Installation

```bash
pip install -e .
```

## Usage

### Basic Commands

```bash
# Create a new window and run a command
tmux-iterm-command create-window --name check --command "python manage.py check"

# List all windows in the current session
tmux-iterm-command list-windows

# Send a command to a specific pane
tmux-iterm-command send --window 0 --pane 0 "ls -la"

# Capture output from a pane
tmux-iterm-command capture-pane --window 0 --pane 0 --lines 50

# Wait for a pane to be idle (no output for 2 seconds, timeout after 30s)
tmux-iterm-command wait-idle --window 0 --pane 0 --quiet-for 2 --timeout 30

# Kill a window
tmux-iterm-command kill-window --window 0
```

### Session and Environment Commands

```bash
# List all tmux sessions (to see what sessions are available)
tmux-iterm-command list-sessions

# Create a new pane by splitting a window
tmux-iterm-command create-pane --window 0 --vertical --command "tail -f logs/app.log"

# Kill a pane
tmux-iterm-command kill-pane --window 0 --pane 1
```

### Environment Detection

```bash
# Detect current environment capabilities
tmux-iterm-command detect

# Check current status
tmux-iterm-command status
```

## Command Reference

### `create-window`
Create a new tmux window with an optional command.
- `--name`: Window name
- `--command`: Optional command to run in the window
- `--shell`: Shell to use (default: /bin/bash)

### `create-pane`
Split a window to create a new pane.
- `--window`: Window index to split
- `--vertical`/`--horizontal`: Split orientation (default: vertical)
- `--command`: Optional command to run in the new pane

### `send`
Send a command to a specific pane.
- `--window`: Window index
- `--pane`: Pane index
- `--no-enter`: Don't send Enter after command

### `capture-pane`
Capture output from a pane.
- `--window`: Window index
- `--pane`: Pane index
- `--lines`: Number of lines to capture (default: 100)

### `wait-idle`
Wait for a pane to be idle.
- `--window`: Window index
- `--pane`: Pane index
- `--timeout`: Max time to wait in seconds (default: 30)
- `--quiet-for`: Seconds of no output to consider idle (default: 2)
- `--poll-interval`: Polling interval in seconds (default: 0.1)

### `kill-window`
Kill a tmux window.
- `--window`: Window index to kill

### `kill-pane`
Kill a tmux pane.
- `--window`: Window index containing the pane
- `--pane`: Pane index to kill

### `list-sessions`
List all tmux sessions.

### `list-windows`
List all windows in the current session.
- `--session`: Optional session name to list windows from

### `list-panes`
List all panes in a specific window.
- `--window`: Window index

### `set-badge`
Set iTerm2 badge for a window (placeholder - requires iTerm2 integration).
- `--window`: Window index
- `--text`: Badge text

### `set-mark`
Set iTerm2 mark for a pane (placeholder - requires iTerm2 integration).
- `--window`: Window index
- `--pane`: Pane index

### `notify`
Send notification (placeholder - requires iTerm2 integration).
- `--message`: Notification message
- `--title`: Notification title (default: 'tmux-iterm-command')

### `set-tab-color`
Set iTerm2 tab color (placeholder - requires iTerm2 integration).
- `--window`: Window index
- `--red`: Red value (0-255, default: 0)
- `--green`: Green value (0-255, default: 0)
- `--blue`: Blue value (0-255, default: 0)

### `detect`
Detect environment capabilities.
- No arguments required

### `status`
Show current tmux status (equivalent to list-windows).
- No arguments required

## Output Format

All commands return JSON output with a consistent structure:

```json
{
  "status": "success",
  "data": { ... }
}
```

Or in case of error:

```json
{
  "status": "error",
  "message": "Error description",
  "code": "ERROR_CODE"
}
```

This makes it easy for coding agents to parse and understand the results.

## For Coding Agents

This tool is specifically designed for coding agents to:
1. Create isolated environments for different tasks
2. Run long-running processes (like development servers)
3. Monitor output from background processes
4. Execute multiple commands concurrently in different panes
5. Capture and analyze command output

The JSON output format allows agents to programmatically respond to command results and manage complex terminal-based workflows.