# Recommendation: Interactive Terminal Management for CLAUDE.md

## Interactive Terminal Management with tmux-iterm-command

This project uses `tmux-iterm-command` for managing interactive terminal sessions. Use this tool when:

- Running interactive commands that require user input (e.g., interactive scripts, Django shell_plus)
- Starting long-running server processes (e.g., dev servers, test runners with live output)
- Interactive debugging (e.g., pdb, Node inspect, gdb - stepping through code)
- Running commands that generate continuous output (logs, real-time updates)

**DO NOT use this tool for:** Simple one-off commands, build scripts, or operations that complete quickly.

### Common Workflows

#### Starting a Development Server

```bash
# Create a new window for the dev server
uvx git+https://github.com/joej/tmux-iterm-command create-window \
  --name "dev-server" \
  --command "python manage.py runserver"

# Later, send additional commands to that window
uvx git+https://github.com/joej/tmux-iterm-command send \
  --window 1 --pane 0 \
  "# Restart the server"
```

#### Running Interactive Django Shell

```bash
# Create window for Django shell session
uvx git+https://github.com/joej/tmux-iterm-command create-window \
  --name "django-shell" \
  --command "python manage.py shell_plus"

# Send Python commands to the shell
uvx git+https://github.com/joej/tmux-iterm-command send \
  --window 2 --pane 0 \
  "User.objects.all()"

# Capture output
uvx git+https://github.com/joej/tmux-iterm-command capture-pane \
  --window 2 --pane 0 --lines 50
```

#### Debugging with pdb

```bash
# Create a window for debugging
uvx git+https://github.com/joej/tmux-iterm-command create-window \
  --name "debug" \
  --command "python -m pdb script.py"

# Step through code interactively
uvx git+https://github.com/joej/tmux-iterm-command send \
  --window 3 --pane 0 "n"  # next
```

#### Splitting a Window for Multiple Tasks

```bash
# Create horizontal split to run two commands side-by-side
uvx git+https://github.com/joej/tmux-iterm-command create-pane \
  --window 0 --horizontal \
  --command "npm run watch"

# Send command to the new pane
uvx git+https://github.com/joej/tmux-iterm-command send \
  --window 0 --pane 1 \
  "npm run dev"
```

#### Monitoring Command Output

```bash
# Wait for a process to stabilize before checking output
uvx git+https://github.com/joej/tmux-iterm-command wait-idle \
  --window 0 --pane 0 \
  --quiet-for 2 --timeout 30

# Capture the last 100 lines
uvx git+https://github.com/joej/tmux-iterm-command capture-pane \
  --window 0 --pane 0 --lines 100
```

### Session Management

The tool automatically manages the 'claude-dev' default session. You can:
- List existing windows: `uvx git+https://github.com/joej/tmux-iterm-command list-windows`
- List panes in a window: `uvx git+https://github.com/joej/tmux-iterm-command list-panes --window 0`
- Kill a window: `uvx git+https://github.com/joej/tmux-iterm-command kill-window --window 1`
- Kill a pane: `uvx git+https://github.com/joej/tmux-iterm-command kill-pane --window 0 --pane 1`

### Tips

- Always use `--quiet-for` and `--timeout` with `wait-idle` to avoid hanging
- Use `capture-pane --lines` to get recent output after commands complete
- Send `--no-enter` flag if you need to construct a command without executing it immediately
- Use meaningful `--name` values for windows so you can identify them later

---

## Key Points for Implementation

1. **Be explicit about use cases** - Help other Claude instances understand when to use vs. not use the tool
2. **Provide concrete examples** - Show actual uvx command patterns they can copy/adapt
3. **Document the workflow** - Show the typical sequence: create → send → capture
4. **Include session patterns** - How to work with multiple windows/panes
5. **Add tips section** - Common gotchas and best practices

You can also add project-specific guidance like:
- Which services typically run long (server, database, watchers)
- Which commands need interactive input
- Recommended window naming scheme for your team
- Any custom aliases or helpers you've created
