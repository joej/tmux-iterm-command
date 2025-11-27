# How tmux-iterm-command Works with Agentic Coding Tools

This document explains how an agentic coding tool (like Claude Code, Gemini, Codex, Qwen Code, etc.) will interact with the `tmux-iterm-command` tool.

## 1. Decision Process for When to Use tmux-iterm-command

An agentic coding tool will decide to use `tmux-iterm-command` when it needs to:

- **Run long-running processes** like development servers, watchers, or background services that need to persist beyond the current interaction
- **Execute shell commands** that should continue running while the agent performs other tasks
- **Isolate command execution** to prevent conflicts with the main terminal environment
- **Run multiple concurrent processes** in separate windows/panes for better organization
- **Capture and analyze command output** programmatically without requiring user intervention
- **Maintain session persistence** across terminal disconnections

The agent evaluates the command it needs to run and if it meets criteria like:
- Long-running nature (e.g., `python manage.py runserver`, `npm run dev`)
- Need for continuous monitoring (e.g., `tail -f logs/app.log`)
- Output analysis requirements (e.g., running tests, checking system status)
- Process isolation (e.g., avoiding terminal state changes)

Then it chooses `tmux-iterm-command` over direct shell execution.

## 2. Calling the Command to Open a New Window to Run a Command

When the agent decides to run a command in a separate tmux window, it executes:

```bash
result=$(tmux-iterm-command create-window --name "runserver" --command "python manage.py runserver")
```

The agent parses the JSON response to get the window identifier:

```json
{
  "status": "success",
  "window_id": "@1:2.0",
  "window_index": 2,
  "pane_id": "%0",
  "name": "runserver",
  "session": "claude-dev",
  "inside_tmux": false
}
```

The agent extracts the `window_index` (2 in this example) for future operations. The tool uses a "shell-first" pattern, starting a shell environment before executing the specified command, which prevents output loss and maintains proper command execution context.

For more complex scenarios, the agent can create a window with a specific shell:

```bash
result=$(tmux-iterm-command create-window --name "django-check" --command "python manage.py check" --shell "/bin/bash")
```

## 3. How the Coding Tool Gets the Output of Commands

The agentic coding tool uses the `capture-pane` command to retrieve output from the window. Since tmux operations are asynchronous, the agent typically:

1. **Waits for command completion** using `wait-idle`:
```bash
tmux-iterm-command wait-idle --window 2 --pane 0 --timeout 30 --quiet-for 2
```

2. **Captures the pane output**:
```bash
output=$(tmux-iterm-command capture-pane --window 2 --pane 0 --lines 50)
```

The `wait-idle` command blocks until the pane has been quiet for the specified duration (2 seconds in this example) or the timeout (30 seconds) is reached. This ensures the agent waits for command completion before capturing output.

The JSON response includes the captured content:
```json
{
  "status": "success",
  "content": "Django version 4.2, using settings 'myproject.settings'\nStarting development server at http://127.0.0.1:8000/\n",
  "lines": 20,
  "window_index": 2,
  "pane_index": 0,
  "session": "claude-dev"
}
```

For continuous monitoring, the agent can repeatedly capture output:
```bash
while [ condition ]; do
  output=$(tmux-iterm-command capture-pane --window 2 --pane 0 --lines 10)
  # Process output as needed
  sleep 2
done
```

For immediate command feedback (like sending a command to a shell), the agent can:
1. Use `send-command` to send input to a pane
2. Wait for idle state
3. Capture the updated output

This approach allows the agent to programmatically analyze command results, check for errors, or verify command completion.

## 4. How the Coding Tool Closes the Window When Done

When the agent has completed its task or no longer needs the window, it uses the `kill-window` command:

```bash
result=$(tmux-iterm-command kill-window --window 2)
```

The JSON response confirms the operation:
```json
{
  "status": "success",
  "window_index": 2,
  "session": "claude-dev"
}
```

For cleanup scenarios, the agent may:

1. **Check if the window still exists**:
```bash
windows=$(tmux-iterm-command list-windows)
```

2. **Kill specific windows** when done:
```bash
tmux-iterm-command kill-window --window 2
```

3. **Kill multiple windows** if needed:
```bash
for win in 1 2 3; do
  tmux-iterm-command kill-window --window $win
done
```

For long-running processes, the agent may choose to leave the window running if the process provides ongoing value (like a development server that should continue running for the user), but for one-time commands, the agent will typically clean up by killing the window when its analysis is complete.

In cases where the agent is managing multiple panes within a window, it can use `kill-pane` specifically:
```bash
tmux-iterm-command kill-pane --window 2 --pane 1
```

The agent maintains a state tracking system to keep track of which windows were created by which operations and cleans them up when no longer needed or when the coding session completes.

## Important Note

⚠️ **CRITICAL**: The `tmux-iterm-command` tool operates within existing tmux sessions only. It does NOT create, destroy, or manage tmux sessions. It only manages windows and panes within existing sessions.