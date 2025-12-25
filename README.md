# tmux-iterm-command - Enhanced Terminal Management for AI Coding Agents

A powerful command-line tool designed specifically for AI coding assistants (Claude, Qwen, etc.) to manage tmux windows and panes with enhanced iTerm2 integration for macOS users.

## Why This Tool Exists

AI coding agents often need to:
- Run long-lived processes (like development servers) 
    which the coding agent and the developer can watch see
- Execute concurrent commands across multiple terminals
- Interaction between a coding agent and a CLI command
    and decide what to send, based on what was output
- Capture and analyze command output programmatically
- Manage complex terminal workflows

This tool provides a structured interface that makes these operations safe and reliable.

## Key Benefits for macOS iTerm2 Users

### 🚀 Enhanced iTerm2 Integration
- Creates visible tabs, windows on the desktop via iTerm's tmux integration
- Potential for advanced integration, badge notifications, tab colors, and custom marks
- Optimized for macOS terminal workflows

### 🛡️ Safety-First Design
- **Cannot create or destroy tmux sessions** - only manages windows and panes
  within a session

### 📊 Structured Output
- All commands return JSON for easy parsing by AI agents
- Consistent response format for reliable automation
- Error handling with clear status codes

## Quick Start

### Installation Options

**Install via pip from GitHub:**
```bash
pip install git+https://github.com/joej/tmux-iterm-command.git
```

**Install via uv:**
```bash
uv add git+https://github.com/joej/tmux-iterm-command.git
```

**Run without installation (uvx):**
```bash
uvx git+https://github.com/joej/tmux-iterm-command tmux-iterm-command create-window --name test --command "echo hello"
```

### Basic Usage Examples

**Create a development server window:**
```bash
tmux-iterm-command create-window --name django-server --command "cd /path/to/project && python manage.py runserver 0.0.0.0:8000"
```

**Run concurrent commands in split panes:**
```bash
# Create a new pane in window 0
tmux-iterm-command create-pane --window 0 --vertical --command "tail -f logs/app.log"

# Send commands to specific panes
tmux-iterm-command send --window 0 --pane 1 "pytest tests/"
```

**Capture and analyze output:**
```bash
# Wait for command to complete
tmux-iterm-command wait-idle --window 0 --pane 0 --timeout 30

# Capture the output
tmux-iterm-command capture-pane --window 0 --pane 0 --lines 50
```

**Manage your terminal workspace:**
```bash
# List all windows in current session
tmux-iterm-command list-windows

# Kill a window when done (using window name or index)
tmux-iterm-command kill-window --window 0
# OR
tmux-iterm-command kill-window --window django-server
```

## Django-Specific Example Workflow

Here's a complete example of managing a Django development environment:

```bash
# 1. Create a window for the Django development server
tmux-iterm-command create-window --name django-server --command "cd /path/to/django/project && source venv/bin/activate && python manage.py runserver 0.0.0.0:8000"

# 2. Wait for the server to start
tmux-iterm-command wait-idle --window django-server --pane 0 --timeout 30 --quiet-for 3

# 3. Create a second pane for running tests
tmux-iterm-command create-pane --window django-server --horizontal --command "cd /path/to/django/project && source venv/bin/activate && bash"

# 4. Run tests in the second pane
tmux-iterm-command send --window django-server --pane 1 "python manage.py test"

# 5. Check the server output after running tests
tmux-iterm-command capture-pane --window django-server --pane 0 --lines 20

# 6. Run database migrations in a new window
tmux-iterm-command create-window --name django-db --command "cd /path/to/django/project && source venv/bin/activate && python manage.py migrate"

# 7. When done, kill the server window
tmux-iterm-command kill-window --window django-server
```

## Command Reference

### Window Management
- `create-window` - Create new tmux windows with optional commands
- `kill-window` - Safely destroy windows (accepts window index or name)
- `list-windows` - View all windows in session

### Pane Management  
- `create-pane` - Split windows to create new panes
- `kill-pane` - Remove specific panes
- `list-panes` - View all panes in a window

### Command Execution
- `send` - Send commands to specific panes (accepts window index or name)
- `capture-pane` - Get output from panes (accepts window index or name)
- `wait-idle` - Wait for command completion (accepts window index or name)

### Environment Detection
- `list-sessions` - View all available tmux sessions
- `detect` - Check environment capabilities
- `status` - Get current session status (equivalent to list-windows)

## Advanced Usage Examples

### Working with Windows by Name vs Index

```bash
# Create a window with a name
tmux-iterm-command create-window --name my-project --command "bash"

# List windows to see the assigned index
tmux-iterm-command list-windows

# Send commands using the window name
tmux-iterm-command send --window my-project --pane 0 "ls -la"

# Or using the window index
tmux-iterm-command send --window 2 --pane 0 "pwd"

# List panes in a window by name
tmux-iterm-command list-panes --window my-project
```

### Multi-Pane Workflow

```bash
# Create a window with a command
tmux-iterm-command create-window --name multi-task --command "bash"

# Create a vertical split (new pane will be pane 1)
tmux-iterm-command create-pane --window multi-task --vertical --command "htop"

# Send a command to pane 0 (original pane)
tmux-iterm-command send --window multi-task --pane 0 "tail -f /var/log/app.log"

# Send a command to pane 1 (newly created pane)
tmux-iterm-command send --window multi-task --pane 1 "git status"

# Capture output from both panes
tmux-iterm-command capture-pane --window multi-task --pane 0 --lines 10
tmux-iterm-command capture-pane --window multi-task --pane 1 --lines 10
```

## macOS iTerm2 Specific Features

### Visual Enhancements (Future Integration)
- **Tab Color Coding**: Different colors for different types of operations
- **Badge Notifications**: Status updates directly in iTerm2 tabs
- **Custom Marks**: Visual indicators for important command outputs

### Workflow Optimization
- Optimized for iTerm2's split pane workflows
- Integration with macOS clipboard and notifications
- Terminal profile optimization for AI coding tasks

## Safety Guarantees

This tool is designed with your safety in mind:

✅ **No Session Destruction** - Cannot accidentally kill your tmux sessions  
✅ **No Session Creation** - Works only with existing sessions  
✅ **Isolated Operations** - Only affects targeted windows/panes  
✅ **Predictable Behavior** - Consistent JSON responses for AI consumption  

## For AI Coding Agents

This tool is specifically designed to enhance AI coding workflows:

- **Concurrent Task Management**: Run multiple commands simultaneously
- **Output Analysis**: Capture and process command output programmatically  
- **Environment Consistency**: Maintain consistent shell environments
- **Resource Management**: Clean up windows/panes when tasks complete

## Requirements

- **macOS** (optimized for iTerm2)
- **tmux** installed and running
- **Python 3.7+** for the command-line interface

## Getting Started

1. Ensure you have a tmux session running: `tmux new-session -s coding -d`
2. Install using your preferred method (pip, uv, or uvx)
3. Start managing windows and panes: `tmux-iterm-command create-window --name dev --command "bash"`

## Why macOS Users Love This

- **iTerm2 Integration**: Leverages iTerm2's advanced terminal features
- **Workflow Optimization**: Perfect for complex development workflows
- **Safety**: Protects your existing tmux sessions while enabling AI automation
- **Power**: Enables sophisticated multi-terminal AI coding scenarios

---

*Perfect for developers using AI coding assistants who want safe, reliable terminal management with macOS and iTerm2 optimization.*
