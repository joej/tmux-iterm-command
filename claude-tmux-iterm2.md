# tmux-iterm-command - Tmux Command Tool for Coding Agents

⚠️ **CRITICAL FOR CODING AGENTS**: This tool manages **WINDOWS AND PANES ONLY**. DO NOT create, destroy, or manage tmux SESSIONS. The tool handles session management automatically. If you're trying to manage sessions, you're using this tool wrong.

**Project Name**: `tmux-iterm-command`
**Purpose**: Enable coding agents (Claude, Qwen, Gemini, Codex) to manage tmux **windows and panes** (NOT sessions) for interactive command execution, background processes, and terminal workflows
**Target User**: tmux users running coding agents (Claude, Qwen, Gemini, Codex)
**Primary Use Case**: Development workflows with runserver, shell, and interactive commands (within existing sessions)

---

## Research Summary

### Existing Solutions Analyzed

#### 1. pchalasani/claude-code-tools - tmux-cli
- **URL**: https://github.com/pchalasani/claude-code-tools
- **Approach**: Bash wrapper with simple command interface
- **Architecture**: Detects local vs remote tmux, automatically handles pane management
- **Key Features**:
  - Launch commands in tmux panes
  - Send input with configurable delays
  - Capture output from panes
  - Wait for idle state
  - Interrupt/escape signals
- **Strengths**: Simple, lightweight, no dependencies beyond bash/tmux
- **Limitations**: Basic functionality, no window templates, limited state management

#### 2. michael-abdo/tmux-claude-mcp-server
- **Approach**: Full MCP server for hierarchical Claude instance orchestration
- **Architecture**: Bridge pattern - single MCP server + lightweight bridge for multi-instance access
- **Key Features**:
  - Spawn/manage multiple Claude Code instances
  - Role-based access (Executive/Manager/Specialist)
  - External JSON state store
  - Hierarchical naming (`exec_1`, `mgr_1_1`, `spec_1_1_1`)
  - Workflow automation
- **Strengths**: Advanced orchestration, memory efficient (85% reduction vs multi-server)
- **Limitations**: Complex, focused on Claude-to-Claude communication, not general-purpose

#### 3. nickgnd/tmux-mcp
- **Approach**: MCP server for tmux control
- **Architecture**: TypeScript/JavaScript MCP server
- **Key Features**:
  - List/search sessions
  - View windows/panes
  - Capture terminal content
  - Execute commands
  - Create sessions/windows
  - Split panes
  - Kill sessions/windows/panes
- **Strengths**: Clean MCP interface, good for monitoring
- **Limitations**: No workflow management, basic command execution

#### 4. blle.co/blog/claude-code-tmux-beautiful-terminal
- **URL**: https://www.blle.co/blog/claude-code-tmux-beautiful-terminal
- **Approach**: Conceptual guide for tmux + Claude Code workflow
- **Key Points**:
  - Use tmux for session persistence
  - Long-lived windows for logs, servers, tests
  - iTerm2 integration benefits
  - Manual workflow optimization
- **Takeaway**: Validated need for long-lived vs ephemeral window types

---

## Technical Architecture

### Recommended Approach: Python Library + CLI

**Why Python Library**:
- Mature ecosystem (libtmux)
- Direct Python interface to tmux (no subprocess calls)
- Type hints for maintainability
- Easy testing
- Cross-platform support
- Can package as standalone CLI tool for coding agents

### Technology Stack

```toml
[project]
name = "claude-tmux"
version = "0.1.0"
description = "tmux window manager for Claude Code + iTerm2"
requires-python = ">=3.11"

dependencies = [
    "libtmux>=0.37.0",       # tmux programmatic control
    "click>=8.1.7",          # CLI framework
    "rich>=13.7.0",          # Terminal formatting/tables
    "pydantic>=2.5.0",       # Data validation & serialization
    "watchdog>=3.0.0",       # File system monitoring (for output)
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.9",
    "mypy>=1.7.0",
]
```

### Core Libraries Rationale

**libtmux** (Foundation)
- 1.1k stars, mature codebase
- Object-oriented API: `Server → Session → Window → Pane`
- Type hints throughout
- Powers tmuxp (tmux workspace manager)
- Active maintenance
- Better than raw tmux commands or Control Mode parsing

**Click** (CLI)
- Industry standard for Python CLIs
- Auto-generated help text
- Argument validation
- Shell completion support
- Django's manage.py uses Click patterns

**Rich** (Terminal UI)
- Beautiful tables and progress bars
- Syntax highlighting for output
- Console markup (colors, styles)
- Works well with iTerm2

**Pydantic** (Data)
- Type-safe configuration
- JSON serialization/deserialization
- Validation for state files
- Matches Django's approach

---

## Project Structure

```
claude-tmux/
├── README.md                    # Quick start guide
├── ARCHITECTURE.md              # Design decisions document
├── pyproject.toml               # Project configuration
├── LICENSE                      # MIT or Apache 2.0
├── .gitignore
│
├── src/
│   └── tmux_iterm_command/
│       ├── __init__.py          # Package exports
│       ├── cli.py               # Click CLI interface
│       ├── manager.py           # WindowManager class (core)
│       ├── window.py            # Window abstraction
│       ├── output.py            # OutputCapture + monitoring
│       ├── iterm2.py            # iTerm2Integration class
│       ├── config.py            # Configuration management
│       ├── state.py             # State persistence (JSON/SQLite)
│       └── django.py            # Django-specific helpers
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # pytest fixtures
│   ├── test_manager.py
│   ├── test_window.py
│   ├── test_output.py
│   ├── test_iterm2.py
│   ├── test_django.py
│   └── test_cli.py
│
└── docs/
    ├── getting-started.md
    ├── django-workflows.md
    ├── iterm2-integration.md
    ├── api-reference.md
    └── examples/
        ├── basic-usage.sh
        ├── django-dev.sh
        └── background-jobs.sh
```

---

## Phase 1: MVP Implementation

### Core Features

#### 1. Window Management Commands

```bash
# Create window and run command
tmux-iterm-command create-window [OPTIONS]
  --name TEXT              Named window (default: auto-generated)
  --command TEXT           Command to run in the window
  --shell TEXT             Shell to use (default: /bin/bash)

# Send command to pane
tmux-iterm-command send-command [OPTIONS]
  --window INTEGER         Window index
  --pane INTEGER           Pane index
  --no-enter              Don't press Enter after command (default: press Enter)

# Capture output from pane
tmux-iterm-command capture [OPTIONS]
  --window INTEGER         Window index
  --pane INTEGER           Pane index
  --lines INTEGER          Number of lines to capture (default: 100)

# List sessions
tmux-iterm-command list-sessions

# List windows in current session
tmux-iterm-command list-windows

# List panes in window
tmux-iterm-command list-panes [OPTIONS]
  --window INTEGER         Window index

# Terminate window
tmux-iterm-command kill-window [OPTIONS]
  --window INTEGER         Window index to kill

# Terminate pane
tmux-iterm-command kill-pane [OPTIONS]
  --window INTEGER         Window index containing the pane
  --pane INTEGER           Pane index to kill

# Wait for pane to be idle
tmux-iterm-command wait-idle [OPTIONS]
  --window INTEGER         Window index
  --pane INTEGER           Pane index
  --timeout INTEGER        Max time to wait (default: 30)
  --quiet-for INTEGER      Seconds with no output to consider idle (default: 2)

# Detect environment
tmux-iterm-command detect

# Show current status
tmux-iterm-command status
```

#### 2. Window/Pane Management Concepts

**Default Shell Pattern**
- Windows/panes start with a shell (bash by default)
- Commands are sent to the existing shell environment
- This prevents output loss and maintains environment state
- Example: `tmux-iterm-command create-window --name check --command "python manage.py check"`

**Working Within Sessions**
- The tool operates within existing tmux sessions
- When inside tmux, uses current session
- When outside tmux, creates or connects to default session ('claude-dev')
- Does not create/destroy entire sessions, only manages windows/panes

⚠️ **CRITICAL - CODING AGENTS READ THIS**: You MUST NOT create, destroy, or manage tmux sessions. The tool's built-in session management handles everything automatically. If you see yourself writing code to manage sessions, STOP. You're doing it wrong. Windows and panes only. That's it.

---

## Usage Examples

### Example 1: Django Development Workflow

```bash
# Create window to run Django checks
$ tmux-iterm-command create-window --name check --command "python manage.py check"
{"status": "success", "window_id": "@1:1.0", "window_index": 1, "pane_id": "%0", ...}

# Wait for command to complete
$ tmux-iterm-command wait-idle --window 1 --pane 0 --timeout 10
{"status": "success", "elapsed": 2.5, ...}

# Capture output to see results
$ tmux-iterm-command capture --window 1 --pane 0 --lines 50
{"status": "success", "content": "System check identified no issues...\\n", ...}

# Create window for Django shell
$ tmux-iterm-command create-window --name shell --command "python manage.py shell"
{"status": "success", ...}

# Later, send a command to the shell
$ tmux-iterm-command send-command --window 1 --pane 0 --text "User.objects.count()"
{"status": "success", ...}

# Wait for response and capture output
$ tmux-iterm-command wait-idle --window 1 --pane 0 --quiet-for 1
$ tmux-iterm-command capture --window 1 --pane 0 --lines 10
{"status": "success", "content": ">>> User.objects.count()\\n42\\n>>>\\n"}

# List current windows
$ tmux-iterm-command list-windows
{"status": "success", "session": "claude-dev", "windows": [{"index": 0, "name": "check", ...}, {"index": 1, "name": "shell", ...}]}

# Kill window when done
$ tmux-iterm-command kill-window --window 1
{"status": "success", ...}
```

### Example 2: Server and Monitoring

```bash
# Start Django dev server in a window
$ tmux-iterm-command create-window --name runserver --command "python manage.py runserver 8000"
{"status": "success", ...}

# Check for errors periodically
$ tmux-iterm-command capture --window 0 --pane 0 --lines 20
{"status": "success", "content": "...\\nDjango version 4.2, using settings 'myproject.settings'\\nStarting development server at http://127.0.0.1:8000/\\n...", ...}

# List sessions to see all available sessions
$ tmux-iterm-command list-sessions
{"status": "success", "sessions": [{"id": "@1", "name": "claude-dev", "attached": 1, "windows": 2}]}
```

### Example 3: Multiple Tasks in Parallel

```bash
# Run tests in one window
$ tmux-iterm-command create-window --name tests --command "python -m pytest tests/test_models.py"
{"status": "success", ...}

# Run linter in a split pane of the same window
$ tmux-iterm-command create-pane --window 0 --vertical --command "flake8 myapp/models.py"
{"status": "success", ...}

# Monitor both outputs separately
$ tmux-iterm-command capture --window 0 --pane 0 --lines 10  # Tests output
$ tmux-iterm-command capture --window 0 --pane 1 --lines 10  # Linter output
```

---

## Implementation Details

### Core Classes

#### TmuxManager
```python
import libtmux
from libtmux.server import Server
from libtmux.session import Session
from libtmux.window import Window
from libtmux.pane import Pane

class TmuxManager:
    """Manages tmux operations for coding agents."""

    def __init__(self, session_name: str = "claude-dev", verbose: bool = False):
        self.server = Server()
        self.session_name = session_name
        self.verbose = verbose
        self._session: Optional[Session] = None
        self.inside_tmux = bool(os.environ.get('TMUX'))

        # Handle session detection based on current environment
        if self.inside_tmux:
            # If inside tmux, use the current session
            current_session_id = os.environ.get('TMUX').split(',')[-1]
            sessions = self.server.list_sessions()
            for session in sessions:
                if session.get('session_id') == current_session_id:
                    self._session = session
                    self.session_name = session.get('session_name')
                    break
        else:
            # If outside tmux, get or create the named session
            self._session = self._get_or_create_session(session_name)

    def create_window(self, window_name: str, command: Optional[str] = None,
                     shell: str = "/bin/bash") -> Dict[str, Any]:
        """Create a new window in the session with shell-first pattern."""

    def create_pane(self, window_index: int, vertical: bool = True,
                   command: Optional[str] = None) -> Dict[str, Any]:
        """Split a window to create a new pane."""

    def send_command(self, window_index: int, pane_index: int,
                    command: str, enter: bool = True) -> Dict[str, Any]:
        """Send a command to a specific pane."""

    def capture_pane(self, window_index: int, pane_index: int,
                    lines: int = 100) -> Dict[str, Any]:
        """Capture output from a specific pane."""

    def wait_idle(self, window_index: int, pane_index: int,
                 timeout: int = 30, quiet_for: int = 2) -> Dict[str, Any]:
        """Wait for a pane to be idle (no output for quiet_for seconds)."""

    def list_sessions(self) -> Dict[str, Any]:
        """List all tmux sessions."""

    def list_windows(self, session_name: Optional[str] = None) -> Dict[str, Any]:
        """List all windows in the session."""

    def list_panes(self, window_index: int) -> Dict[str, Any]:
        """List all panes in a specific window."""

    def kill_window(self, window_index: int) -> Dict[str, Any]:
        """Kill a window in the session."""

    def kill_pane(self, window_index: int, pane_index: int) -> Dict[str, Any]:
        """Kill a pane in a specific window."""
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_manager.py
def test_create_window(manager):
    """Test creating a window."""
    result = manager.create_window(window_name="test", command="echo 'hello'")
    assert result["status"] == "success"
    assert "window_id" in result
    assert result["name"] == "test"

def test_send_command(manager):
    """Test sending command to pane."""
    result = manager.create_window(window_name="cmd_test")
    if result["status"] == "success":
        window_idx = result["window_index"]
        cmd_result = manager.send_command(window_index=window_idx, pane_index=0, command="echo test")
        assert cmd_result["status"] == "success"

def test_capture_pane(manager):
    """Test capturing pane output."""
    result = manager.create_window(window_name="capture_test", command="echo 'test output'")
    if result["status"] == "success":
        window_idx = result["window_index"]
        capture_result = manager.capture_pane(window_index=window_idx, pane_index=0, lines=5)
        assert capture_result["status"] == "success"
        assert "test output" in capture_result["content"]
```

---

## Installation & Setup

### Installation

```bash
# Install the package
pip install -e .

# Or install in development mode
pip install -e ".[dev]"
```

### Initial Setup

```bash
# The tool is ready to use immediately
# It will automatically use the current tmux session if inside tmux
# Or create/use the default 'claude-dev' session if outside tmux
ticmd list-sessions
```

### No iTerm2 Setup Required

This tool works with any terminal that supports tmux (tmux is only required dependency).
No special iTerm2 setup is needed for basic functionality.

1. Enable tmux integration: iTerm2 → Preferences → General → tmux
2. Check "Use tmux control mode (-CC) if available"
---

## Benefits for Your Workflow

### For Development Workflows
✅ **Background processes**: Run servers, watchers, and long-running tasks
✅ **Interactive commands**: Execute shell commands in isolated environments
✅ **Output capture**: Capture and analyze command output programmatically
✅ **Multiple tasks**: Run several commands concurrently in separate windows/panes
✅ **Session persistence**: Work continues in tmux even if terminal disconnects

### For Coding Agents
✅ **Structured output**: JSON responses designed for agent consumption
✅ **Reliable operations**: Uses libtmux library for consistent behavior
✅ **Environment aware**: Works both inside and outside tmux sessions
✅ **Simple commands**: Focused set of operations for window/pane management
✅ **No dependencies**: Only requires tmux, works with any terminal

---

## Next Steps

1. Install and test the tool with basic commands
2. Integrate with your coding agent workflows
3. Provide feedback on additional commands needed
4. Explore advanced tmux features as needed

---

## Getting Started (Quick Start)

```bash
# Install
pip install -e .

# Start Django dev server in a new window
cd /path/to/django/project
tmux-iterm-command create-window --name runserver --command "python manage.py runserver"

# List windows
tmux-iterm-command list-windows

# Check output of the runserver window (e.g., window 0, pane 0)
tmux-iterm-command capture --window 0 --pane 0 --lines 20

# Kill window when done
tmux-iterm-command kill-window --window 0
```

---

## Timeline

**Phase 1 (MVP)**: 2-3 days
- Project setup
- Core WindowManager implementation
- CLI interface (launch, send, read, list, kill, attach)
- Django helpers (runserver, shell)
- iTerm2 detection
- Basic tests
- README documentation

---

## References

- **libtmux Documentation**: https://libtmux.git-pull.com/
- **tmux Manual**: `man tmux`
- **Click Documentation**: https://click.palletsprojects.com/

---

**Next Steps**: Install and begin using the tool in your coding agent workflows.
