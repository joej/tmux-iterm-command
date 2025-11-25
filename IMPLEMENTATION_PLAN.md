# tmux-iterm-command: Implementation Plan

## Project Purpose

tmux-iterm-command is a command-line tool for coding agents (Claude, Qwen, Gemini, Codex) to create and manage tmux windows/panes. The tool operates within existing tmux sessions and focuses on window/pane management rather than session lifecycle management.

---

## Learning from Existing Tools

NOTE - these tools' features and approach are informative to us, even though we may not directly adopt them.

### From pchalasani/claude-code-tools (tmux-cli)
✅ **Auto-detect local vs remote tmux** - adapt behavior
✅ **Simple pane IDs** - just numbers, not complex identifiers
✅ **wait_idle command** - block until pane is idle
✅ **interrupt/escape** - send special keys (Ctrl+C, Esc)
✅ **Best practice: Launch shell first** - prevents output loss on command failure
✅ **JSON output** - structured responses for parsing

### From nickgnd/tmux-mcp
✅ **Comprehensive operations** - full lifecycle management
✅ **Session/window/pane creation** - don't assume existing sessions
✅ **Split panes** - not just windows
✅ **Capture pane** - read terminal content
✅ **Execute command pattern** - send and track commands

---

## Architecture

### Technology
- **Python 3.8+** (not bash, not Node.js - clean library integration)
- **libtmux** - tmux programmatic control (Python library, not subprocess calls)
- **Click** - CLI framework
- **JSON output** - all commands return structured data for agents

### Design Patterns

**Session Management:**
```python
# Auto-detect: inside tmux vs outside
if os.environ.get('TMUX'):
    # Inside tmux - use current session
    use_current_session()
else:
    # Outside tmux - connect to or create named session if needed
    get_or_use_session('claude-dev')  # Only for window/pane operations
```
NOTE -- The tool operates within existing tmux sessions and does NOT manage session lifecycle.
It works both inside and outside tmux but does not create/destroy entire sessions.
The focus is on window/pane management within sessions.

**Shell-First Pattern** (from tmux-cli):
```python
# Always launch shell, then send commands to prevent output loss
def safe_execute(command):
    pane = launch_pane("bash")  # Use default shell
    send_to_pane(pane, command)
    return wait_and_capture(pane)
```
NOTE - yes, when creating a new pane or window, we should create it using the
default user shell (e.g., bash). Then, we can run the command that coding
agents need to execute.
E.g., new tmux window with bash; send command "python manage.py
check" which runs and quits. We can read the output because the window or pane
did not close when the command exited. Then, when ready, agent can
close/destroy/terminate the window or pane

---

## Phase 1: Core CLI Commands

### Window/Pane Management

**1. create-window** - Create window with command
```bash
tmux-iterm-command create-window --name "check" [--command "python manage.py check"] [--shell bash]
# Output: {status: success, window_id: "1", name: "check", pane_id: "%0"}
# Pattern: Creates shell first, then sends command if provided
```

**2. create-pane** - Split window into pane
```bash
tmux-iterm-command create-pane --window 1 [--vertical] [--command "tail -f logs/app.log"]
# Output: {status: success, pane_id: "1", orientation: "vertical"}
```

**3. list-sessions** - Show all sessions
```bash
tmux-iterm-command list-sessions
# Output: {status: success, sessions: [{id: "@1", name: "claude-dev", attached: true, windows: 2}]}
```

**4. list-windows** - Show all windows in current session
```bash
tmux-iterm-command list-windows
# Output: {status: success, windows: [{index: 0, name: "check", active: true, panes: 1}]}
```

**5. list-panes** - Show panes in window
```bash
tmux-iterm-command list-panes --window 1
# Output: {status: success, panes: [{id: "%0", index: 0, active: true, height: 24, width: 80}]}
```

### Command Execution & Interaction

**6. send-command** - Send command to pane
```bash
tmux-iterm-command send-command --window 1 --pane 0 --text "ls -la" [--no-enter]
# Output: {status: success, command: "ls -la", window_index: 1, pane_index: 0}
```

**7. capture** - Read pane output
```bash
tmux-iterm-command capture --window 1 --pane 0 [--lines 100]
# Output: {status: success, content: "...", lines: 100, window_index: 1, pane_index: 0}
```

**8. wait-idle** - Wait for pane to be idle
```bash
tmux-iterm-command wait-idle --window 1 --pane 0 [--timeout 30] [--quiet-for 2]
# Output: {status: success, elapsed: 3.2, window_index: 1, pane_index: 0}
# Blocks until no output for N seconds
```

### Lifecycle Management (Windows/Panes only)

**9. kill-window** - Close window
```bash
tmux-iterm-command kill-window --window 1
# Output: {status: success, window_index: 1}
```

**10. kill-pane** - Close pane
```bash
tmux-iterm-command kill-pane --window 1 --pane 1
# Output: {status: success, window_index: 1, pane_index: 1}
```

NOTE - Session lifecycle is NOT managed by this tool.
The tool operates within existing tmux sessions and only manages windows/panes.

### Environment Detection

**11. detect** - Show environment capabilities
```bash
tmux-iterm-command detect
# Output: {
#   status: "success",
#   iterm2: false,
#   tmux: true,
#   shell_integration: true,
#   session: "claude-dev",
#   inside_tmux: false
# }
```

**12. status** - Show current session state
```bash
tmux-iterm-command status
# Output: {
#   status: "success",
#   windows: [...],
#   session: "claude-dev"
# }
```

---

## Core Implementation Classes

### TmuxManager
```python
class TmuxManager:
    def __init__(self, session_name="claude-dev", verbose=False):
        self.server = libtmux.Server()
        self.verbose = verbose
        self.inside_tmux = bool(os.environ.get('TMUX'))
        self.session_name = session_name
        self._session = None

        # Check if we're inside a tmux session already
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

    def _get_or_create_session(self, session_name: str):
        """Get existing session or create a new one."""
        sessions = self.server.list_sessions()
        for session in sessions:
            if session.get('session_name') == session_name:
                return session
        return self.server.new_session(session_name=session_name, attach=False)

    def create_window(self, window_name: str, command=None, shell="/bin/bash"):
        # Shell-first pattern to prevent output loss
        window = self.session.new_window(window_name=window_name, attach=False)
        pane = window.attached_pane

        if not pane:
            raise RuntimeError("No attached pane found in new window")

        # Launch shell first
        pane.send_keys(shell, enter=True)
        time.sleep(0.2)

        # Send command if provided
        if command:
            pane.send_keys(command, enter=True)

        return {
            'status': 'success',
            'window_id': f"{self.session.session_id}:{window.index}",
            'window_index': int(window.index),
            'pane_id': pane.pane_id,
            'name': window_name,
            'session': self.session_name
        }

    def send_command(self, window_index: int, pane_index: int, command: str, enter=True):
        window = self.session.find_windows({'window_index': str(window_index)})
        if not window:
            return {'status': 'error', 'message': f'Window {window_index} not found'}
        window = window[0]

        # Find the pane by index within the window
        panes = window.panes
        target_pane = None
        for pane in panes:
            if pane.pane_index == str(pane_index):
                target_pane = pane
                break

        if not target_pane:
            return {'status': 'error', 'message': f'Pane {pane_index} not found in window {window_index}'}

        target_pane.send_keys(command, enter=enter)
        return {
            'status': 'success',
            'command': command,
            'window_index': window_index,
            'pane_index': pane_index
        }

    def capture_pane(self, window_index: int, pane_index: int, lines: int = 100):
        window = self.session.find_windows({'window_index': str(window_index)})
        if not window:
            return {'status': 'error', 'message': f'Window {window_index} not found'}
        window = window[0]

        # Find the pane by index within the window
        panes = window.panes
        target_pane = None
        for pane in panes:
            if pane.pane_index == str(pane_index):
                target_pane = pane
                break

        if not target_pane:
            return {'status': 'error', 'message': f'Pane {pane_index} not found in window {window_index}'}

        # Capture pane content
        result = target_pane.capture_pane(pane_index=str(pane_index), suppress_empty=True)
        if result is None:
            result = []

        # Only return the requested number of lines from the end
        if len(result) > lines:
            result = result[-lines:]

        output = '\n'.join(result) if result else ''

        return {
            'status': 'success',
            'content': output,
            'lines': len(result),
            'window_index': window_index,
            'pane_index': pane_index
        }

    def wait_idle(self, window_index: int, pane_index: int, timeout: int = 30, quiet_for: int = 2):
        window = self.session.find_windows({'window_index': str(window_index)})
        if not window:
            return {'status': 'error', 'message': f'Window {window_index} not found'}
        window = window[0]

        # Find the pane by index within the window
        panes = window.panes
        target_pane = None
        for pane in panes:
            if pane.pane_index == str(pane_index):
                target_pane = pane
                break

        if not target_pane:
            return {'status': 'error', 'message': f'Pane {pane_index} not found in window {window_index}'}

        start_time = time.time()
        last_content = ""
        last_change_time = start_time

        while time.time() - start_time < timeout:
            current_content = target_pane.capture_pane(pane_index=str(pane_index), suppress_empty=True)
            if current_content is None:
                current_content = []
            current_content_str = '\n'.join(current_content) if current_content else ''

            if current_content_str != last_content:
                last_content = current_content_str
                last_change_time = time.time()
            elif time.time() - last_change_time >= quiet_for:
                elapsed = time.time() - start_time
                return {
                    'status': 'success',
                    'elapsed': elapsed,
                    'window_index': window_index,
                    'pane_index': pane_index
                }

            time.sleep(0.1)

        elapsed = time.time() - start_time
        return {
            'status': 'timeout',
            'elapsed': elapsed,
            'timeout': timeout,
            'window_index': window_index,
            'pane_index': pane_index
        }
```

---

## Project Structure

```
claude-iterm-tmux/
├── CLAUDE.md                 # Already created
├── pyproject.toml
├── requirements.txt          # libtmux, click
├── README.md
├── .gitignore
│
├── src/
│   └── tmux_iterm_command/
│       ├── __init__.py
│       ├── cli.py            # Click commands (entry point)
│       ├── manager.py        # TmuxManager class
│       ├── iterm2.py         # iTerm2Escape class
│       ├── shell_int.py      # ShellIntegration class
│       └── utils.py          # Helper functions
│
└── tests/
    ├── __init__.py
    ├── conftest.py           # Fixtures for tmux sessions
    ├── test_manager.py
    ├── test_iterm2.py
    └── test_cli.py
```

---

## Usage Examples (Coding Agent Workflow)

### Example 1: Validate Django Fix
```bash
# Create window with shell, run check
result=$(tmux-iterm-command create-window --name check --command "python manage.py check" --shell bash)
window=$(echo $result | jq -r '.window_index')

# Wait for completion
tmux-iterm-command wait-idle --window $window --pane 0 --timeout 10

# Read output
output=$(tmux-iterm-command capture --window $window --pane 0 --lines 50)

# Parse result
if echo "$output" | grep -q "System check identified no issues"; then
    echo "✓ Check passed!"
else
    echo "✗ Check failed"
fi

# Close window
tmux-iterm-command kill-window --window $window
```

### Example 2: Interactive Shell Query
```bash
# Create shell window
result=$(tmux-iterm-command create-window --name shell --command "python manage.py shell")
window=$(echo $result | jq -r '.window_index')

# Wait for shell to start
tmux-iterm-command wait-idle --window $window --pane 0 --timeout 5

# Send query
tmux-iterm-command send-command --window $window --pane 0 --text "User.objects.count()"

# Wait for result
tmux-iterm-command wait-idle --window $window --pane 0 --quiet-for 1

# Read result
output=$(tmux-iterm-command capture --window $window --pane 0 --lines 20)
echo "Result: $output"

# Close
tmux-iterm-command kill-window --window $window
```

### Example 3: Long-Running Server
```bash
# Start server
result=$(tmux-iterm-command create-window --name runserver --command "python manage.py runserver")
window=$(echo $result | jq -r '.window_index')

# Later: check for errors
output=$(tmux-iterm-command capture --window $window --pane 0 --lines 100)
if echo "$output" | grep -qE "ERROR|Exception"; then
    echo "Server has errors!"
fi

# Keep window alive - don't kill
```

---

## Success Criteria (Phase 1)

✅ Create/manage tmux windows and panes
✅ Send commands and read output
✅ Wait for command completion (wait-idle)
✅ Send special keys (Ctrl+C, Escape)
✅ Auto-detect local vs remote tmux
✅ Shell-first pattern to prevent output loss
✅ iTerm2 escape sequences (badges, marks, notifications, colors)
✅ Shell integration detection
✅ Clean JSON output for parsing
✅ Works in both remote SSH and local scenarios
✅ Comprehensive tests

---

## Phase 2 (Future)

- Pattern-based error detection
- Automated triggers on output patterns
- Workspace templates (multiple windows at once)
- State persistence (track long-running windows)
- MCP server wrapper (optional)
- Inline images for test results
- Advanced shell integration parsing
