# Comprehensive tmux-iterm-command Usage Guide

tmux-iterm-command is a powerful tool that enables coding agents and developers to manage tmux windows and panes programmatically. Here's a comprehensive guide with practical command examples:

## Basic Usage Patterns

### Creating Windows for Commands

```bash
# Run a simple command in a new window
tmux-iterm-command create-window --name search --command "find src -name '*.py'"

# Create a window with a specific shell and command
tmux-iterm-command create-window --name grep --command "grep -r 'function_name' src/" --shell "/bin/bash"
```

### Capturing Output

```bash
# Run a command and capture its output
tmux-iterm-command create-window --name "file-search" --command "find . -name '*.py' -type f"
tmux-iterm-command wait-idle --window 0 --pane 0 --timeout 10
tmux-iterm-command capture --window 0 --pane 0 --lines 20

# Search for Python files specifically
tmux-iterm-command create-window --name "py-search" --command "find . -name '*.py' | head -20"
tmux-iterm-command wait-idle --window 0 --pane 0 --timeout 5 --quiet-for 1
tmux-iterm-command capture --window 0 --pane 0
```

### Managing Multiple Tasks

```bash
# Run multiple commands in parallel
tmux-iterm-command create-window --name "backend" --command "python manage.py runserver 8000"
tmux-iterm-command create-window --name "frontend" --command "npm run dev"
tmux-iterm-command create-window --name "tests" --command "python -m pytest --watch"

# List all windows to see current tasks
tmux-iterm-command list-windows
```

## Development Workflows

### Python/Django Development

```bash
# Run Django management commands
tmux-iterm-command create-window --name "migrations" --command "python manage.py makemigrations"
tmux-iterm-command wait-idle --window 0 --pane 0 --timeout 10
tmux-iterm-command capture --window 0 --pane 0

# Run tests in a separate window
tmux-iterm-command create-window --name "tests" --command "python -m pytest tests/test_models.py -v"
tmux-iterm-command create-window --name "shell" --command "python manage.py shell"
tmux-iterm-command send-command --window 1 --pane 0 --text "User.objects.count()"
tmux-iterm-command wait-idle --window 1 --pane 0 --quiet-for 1
tmux-iterm-command capture --window 1 --pane 0 --lines 10
```

### Node.js Development

```bash
# Run development servers
ticmd create-window --name "dev-server" --command "npm run dev"
ticmd create-window --name "build" --command "npm run build -- --watch"

# Lint and run tests simultaneously
ticmd create-window --name "lint" --command "npm run lint"
ticmd create-window --name "test" --command "npm test -- --watch"
```

### System Administration Tasks

```bash
# Monitor system resources while running commands
ticmd create-window --name "system" --command "htop"
ticmd create-window --name "process" --command "find /var/log -name '*.log' -exec tail -f {} +"

# Search for specific files or patterns
ticmd create-window --name "search" --command "find . -type f -name '*.py' -exec grep -l 'import os' {} \;"
ticmd wait-idle --window 1 --pane 0 --timeout 30
ticmd capture --window 1 --pane 0 --lines 50
```

## Long-Running Processes

### Development Servers

```bash
# Start a Django development server in a persistent window
ticmd create-window --name "django-server" --command "python manage.py runserver 8080"
# The server continues running in the background
# Check the server output periodically
ticmd capture --window 0 --pane 0 --lines 10

# Start a Node.js development server
ticmd create-window --name "node-dev" --command "nodemon server.js"
ticmd create-window --name "logs" --command "tail -f ./logs/app.log"

# Monitor both simultaneously
ticmd capture --window 0 --pane 0 --lines 5  # Server output
ticmd capture --window 1 --pane 0 --lines 5  # Log output
```

### Background Building and Watching

```bash
# Continuous build process
ticmd create-window --name "build-watch" --command "webpack --watch"

# Continuous testing
ticmd create-window --name "test-watch" --command "pytest --looponfail"

# Monitor both processes
while true; do
  echo "--- Build Output ---"
  ticmd capture --window 0 --pane 0 --lines 5
  echo "--- Test Output ---"
  ticmd capture --window 1 --pane 0 --lines 5
  sleep 2
done
```

### Database and Service Monitoring

```bash
# Monitor database migrations
ticmd create-window --name "migration" --command "python manage.py migrate --verbosity=2"
ticmd wait-idle --window 0 --pane 0 --timeout 60
if ticmd capture --window 0 --pane 0 | grep -q "error\|Error\|ERROR"; then
  echo "Migration failed!"
  ticmd capture --window 0 --pane 0 --lines 20
fi

# Start a database shell for interactive queries
ticmd create-window --name "db-shell" --command "python manage.py dbshell"
ticmd send-command --window 1 --pane 0 --text "SELECT COUNT(*) FROM auth_user;"
ticmd wait-idle --window 1 --pane 0 --quiet-for 2
ticmd capture --window 1 --pane 0 --lines 10
```

## Command Interaction and Output Capture

### Interactive Shell Commands

```bash
# Create a shell in a window for multiple commands
ticmd create-window --name "interactive" --shell "/bin/bash"
ticmd send-command --window 0 --pane 0 --text "cd /path/to/project"
ticmd send-command --window 0 --pane 0 --text "ls -la"
ticmd wait-idle --window 0 --pane 0 --quiet-for 1
ticmd capture --window 0 --pane 0 --lines 20

# Run a multi-step process
ticmd create-window --name "setup" --shell "/bin/bash"
ticmd send-command --window 0 --pane 0 --text "python -c 'import sys; print(sys.version)'"
ticmd wait-idle --window 0 --pane 0 --quiet-for 1
ticmd send-command --window 0 --pane 0 --text "pip list | grep django"
ticmd wait-idle --window 0 --pane 0 --quiet-for 1
ticmd capture --window 0 --pane 0 --lines 10
```

### File System Operations

```bash
# Search for specific files using find
ticmd create-window --name "find-tasks" --command "find . -name '*.py' -size +10k | head -20"
ticmd wait-idle --window 0 --pane 0 --timeout 10
result=$(ticmd capture --window 0 --pane 0)
echo "Large Python files found:"
echo "$result"

# Search for patterns in files
ticmd create-window --name "grep-search" --command "grep -r 'TODO\|FIXME' --include='*.py' src/"
ticmd wait-idle --window 0 --pane 0 --timeout 30
todo_list=$(ticmd capture --window 0 --pane 0)
echo "TODO/FIXME items found:"
echo "$todo_list"
```

### Error Detection and Monitoring

```bash
# Run tests and monitor for failures
ticmd create-window --name "tests" --command "python -m pytest tests/unit/ -x"
ticmd wait-idle --window 0 --pane 0 --timeout 120 --quiet-for 2
test_output=$(ticmd capture --window 0 --pane 0 --lines 50)

if echo "$test_output" | grep -q "FAILED\|ERROR"; then
  echo "Tests failed, showing last 20 lines:"
  echo "$test_output" | tail -n 20
else
  echo "All tests passed!"
fi

# Monitor for errors in long-running processes
ticmd create-window --name "server" --command "python manage.py runserver 0.0.0.0:8000"
# Later, check for errors
error_check=$(ticmd capture --window 0 --pane 0 --lines 30)
if echo "$error_check" | grep -i "error\|exception\|traceback"; then
  echo "Errors detected in server output:"
  echo "$error_check"
fi
```

### Working with Panes

```bash
# Create a split pane layout
ticmd create-window --name "main" --command "bash"
ticmd create-pane --window 0 --vertical --command "htop"
# Now you have bash in pane 0 and htop in pane 1
ticmd send-command --window 0 --pane 0 --text "ls -la"
ticmd capture --window 0 --pane 0 --lines 10  # Capture bash output
ticmd capture --window 0 --pane 1 --lines 10  # Capture htop-like status

# Create horizontal split
ticmd create-window --name "logs" --command "tail -f /tmp/app.log"
ticmd create-pane --window 1 --horizontal --command "df -h"
```

### Process Management

```bash
# Start and monitor multiple processes
ticmd create-window --name "webserver" --command "python -m http.server 8080"
ticmd create-window --name "watcher" --command "find . -name '*.py' -exec wc -l {} \; | sort -n"
ticmd create-window --name "monitor" --command "bash"  # Interactive shell

# Send commands to check status
ticmd send-command --window 2 --pane 0 --text "curl -I localhost:8080 2>/dev/null | head -n 1"
ticmd wait-idle --window 2 --pane 0 --quiet-for 1
ticmd capture --window 2 --pane 0
```

### Cleanup and Management

```bash
# List all windows before cleanup
ticmd list-windows

# Kill specific windows when done
ticmd kill-window --window 0
ticmd kill-window --window 1

# Check current session status
ticmd status

# List all available sessions (useful when working across multiple sessions)
ticmd list-sessions
```

## Complete Practical Example: Building a Python Project

```bash
# 1. Set up multiple windows for the build process
ticmd create-window --name "environment" --command "python --version && pip list | head -10"
ticmd wait-idle --window 0 --pane 0 --timeout 5
ticmd capture --window 0 --pane 0

# 2. Install dependencies in another window
ticmd create-window --name "install" --command "pip install -r requirements.txt"
ticmd wait-idle --window 1 --pane 0 --timeout 60

# 3. Run tests in parallel
ticmd create-window --name "tests" --command "python -m pytest tests/ --tb=short"
ticmd create-window --name "lint" --command "flake8 . --statistics"

# 4. Wait for completion and check results
ticmd wait-idle --window 2 --pane 0 --timeout 120
ticmd wait-idle --window 3 --pane 0 --timeout 60

# 5. Capture and evaluate results
test_result=$(ticmd capture --window 2 --pane 0 --lines 20)
lint_result=$(ticmd capture --window 3 --pane 0 --lines 20)

if echo "$test_result" | grep -q "failed"; then
  echo "Tests failed:"
  echo "$test_result" | grep -A 5 -B 5 "FAILED\|ERROR"
fi

if [ -n "$lint_result" ] && ! echo "$lint_result" | grep -q "0"; then
  echo "Lint issues found:"
  echo "$lint_result"
fi
```

These examples demonstrate how tmux-iterm-command enables coding agents and developers to orchestrate complex workflows with multiple concurrent processes, monitor outputs, and manage tmux windows/panes programmatically. The tool works within existing tmux sessions and focuses on window and pane operations. The JSON-based output format makes it easy for agents to parse results and make decisions based on command outcomes.