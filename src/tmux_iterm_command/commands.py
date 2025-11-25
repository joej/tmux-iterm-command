"""Command handlers for tmux-iterm-command CLI."""
import click
import json
from typing import Dict, Any, Optional

from .manager import TmuxManager


def output_result(result: Dict[str, Any]) -> None:
    """Output the result in JSON format."""
    print(json.dumps(result))


def _execute_manager_command(ctx, method_name: str, **kwargs) -> None:
    """Execute a manager method and output the result."""
    manager: TmuxManager = ctx.obj['MANAGER']
    method = getattr(manager, method_name)
    result = method(**kwargs)
    output_result(result)



@click.command()
@click.option('--name', required=True, help='Window name')
@click.option('--command', help='Command to run in the window')
@click.option('--shell', default='/bin/bash', help='Shell to use in the window')
@click.pass_context
def create_window(ctx: click.Context, name: str, command: Optional[str], shell: str) -> None:
    """Create a new tmux window."""
    _execute_manager_command(ctx, 'create_window', window_name=name, command=command, shell=shell)


@click.command()
@click.option('--window', 'window_index', type=int, required=True, help='Window index')
@click.option('--vertical/--horizontal', default=True, help='Split orientation')
@click.option('--command', help='Command to run in the new pane')
@click.pass_context
def create_pane(ctx: click.Context, window_index: int, vertical: bool, command: Optional[str]) -> None:
    """Split a window to create a new pane."""
    _execute_manager_command(ctx, 'create_pane', window_index=window_index, vertical=vertical, command=command)


@click.command()
@click.pass_context
def list_sessions(ctx: click.Context) -> None:
    """List all tmux sessions."""
    _execute_manager_command(ctx, 'list_sessions')


@click.command()
@click.option('--session', help='Session name to list windows from')
@click.pass_context
def list_windows(ctx: click.Context, session: Optional[str]) -> None:
    """List all windows in a session."""
    _execute_manager_command(ctx, 'list_windows', session_name=session)


@click.command()
@click.option('--window', 'window_index', type=int, required=True, help='Window index')
@click.pass_context
def list_panes(ctx: click.Context, window_index: int) -> None:
    """List all panes in a window."""
    _execute_manager_command(ctx, 'list_panes', window_index=window_index)


@click.command()
@click.option('--window', 'window_index', type=int, required=True, help='Window index')
@click.option('--pane', 'pane_index', type=int, required=True, help='Pane index')
@click.argument('command')
@click.option('--no-enter', is_flag=True, help='Do not send Enter after command')
@click.pass_context
def send_command(ctx: click.Context, window_index: int, pane_index: int, command: str, no_enter: bool) -> None:
    """Send a command to a pane."""
    _execute_manager_command(ctx, 'send_command',
                            window_index=window_index,
                            pane_index=pane_index,
                            command=command,
                            enter=not no_enter)


@click.command()
@click.option('--window', 'window_index', type=int, required=True, help='Window index')
@click.option('--pane', 'pane_index', type=int, required=True, help='Pane index')
@click.option('--lines', default=100, help='Number of lines to capture')
@click.pass_context
def capture_pane(ctx: click.Context, window_index: int, pane_index: int, lines: int) -> None:
    """Capture output from a pane."""
    _execute_manager_command(ctx, 'capture_pane', window_index=window_index, pane_index=pane_index, lines=lines)


@click.command()
@click.option('--window', 'window_index', type=int, required=True, help='Window index')
@click.option('--pane', 'pane_index', type=int, required=True, help='Pane index')
@click.option('--timeout', default=30, help='Timeout in seconds')
@click.option('--quiet-for', 'quiet_for', default=2, help='Seconds of no output to consider idle')
@click.option('--poll-interval', 'poll_interval', default=0.1, help='Polling interval in seconds')
@click.pass_context
def wait_idle(ctx: click.Context, window_index: int, pane_index: int, timeout: int, quiet_for: int, poll_interval: float) -> None:
    """Wait for a pane to be idle."""
    _execute_manager_command(ctx, 'wait_idle',
                            window_index=window_index,
                            pane_index=pane_index,
                            timeout=timeout,
                            quiet_for=quiet_for,
                            poll_interval=poll_interval)


@click.command()
@click.option('--window', 'window_index', type=int, required=True, help='Window index to kill')
@click.pass_context
def kill_window(ctx: click.Context, window_index: int) -> None:
    """Kill a tmux window."""
    _execute_manager_command(ctx, 'kill_window', window_index=window_index)


@click.command()
@click.option('--window', 'window_index', type=int, required=True, help='Window index')
@click.option('--pane', 'pane_index', type=int, required=True, help='Pane index to kill')
@click.pass_context
def kill_pane(ctx: click.Context, window_index: int, pane_index: int) -> None:
    """Kill a tmux pane."""
    _execute_manager_command(ctx, 'kill_pane', window_index=window_index, pane_index=pane_index)


@click.command()
@click.option('--window', 'window_index', type=int, required=True, help='Window index')
@click.option('--text', required=True, help='Badge text')
@click.pass_context
def set_badge(ctx: click.Context, window_index: int, text: str) -> None:
    """Set iTerm2 badge for a window (placeholder - requires iTerm2 integration)."""
    # This is a placeholder since direct iTerm2 integration isn't reliable
    result = {
        "status": "success",
        "message": f"Badge '{text}' would be set for window {window_index} (requires iTerm2)",
        "window_index": window_index,
        "text": text
    }
    output_result(result)


@click.command()
@click.option('--window', 'window_index', type=int, required=True, help='Window index')
@click.option('--pane', 'pane_index', type=int, required=True, help='Pane index')
@click.pass_context
def set_mark(ctx: click.Context, window_index: int, pane_index: int) -> None:
    """Set iTerm2 mark for a pane (placeholder - requires iTerm2 integration)."""
    result = {
        "status": "success",
        "message": f"Mark would be set for pane {pane_index} in window {window_index} (requires iTerm2)",
        "window_index": window_index,
        "pane_index": pane_index
    }
    output_result(result)


@click.command()
@click.option('--message', required=True, help='Notification message')
@click.option('--title', default='tmux-iterm-command', help='Notification title')
@click.pass_context
def notify(ctx: click.Context, message: str, title: str) -> None:
    """Send notification (placeholder - requires iTerm2 integration)."""
    result = {
        "status": "success",
        "message": f"Notification would be sent: {title} - {message} (requires iTerm2)",
        "title": title
    }
    output_result(result)


@click.command()
@click.option('--window', 'window_index', type=int, required=True, help='Window index')
@click.option('--red', default=0, help='Red value (0-255)', type=int)
@click.option('--green', default=0, help='Green value (0-255)', type=int)
@click.option('--blue', default=0, help='Blue value (0-255)', type=int)
@click.pass_context
def set_tab_color(ctx: click.Context, window_index: int, red: int, green: int, blue: int) -> None:
    """Set iTerm2 tab color (placeholder - requires iTerm2 integration)."""
    result = {
        "status": "success",
        "message": f"Tab color would be set for window {window_index} (requires iTerm2)",
        "window_index": window_index,
        "color": {"r": red, "g": green, "b": blue}
    }
    output_result(result)


@click.command()
@click.pass_context
def detect(ctx: click.Context) -> None:
    """Detect environment capabilities."""
    import os

    result = {
        "status": "success",
        "iterm2": os.environ.get('TERM_PROGRAM') == 'iTerm.app',
        "tmux": bool(os.environ.get('TMUX')),
        "shell_integration": any([
            os.path.exists(os.path.expanduser('~/.iterm2_shell_integration.bash')),
            os.path.exists(os.path.expanduser('~/.iterm2_shell_integration.zsh'))
        ]),
        "session": ctx.obj.get('SESSION', 'claude-dev'),
        "inside_tmux": bool(os.environ.get('TMUX'))
    }
    output_result(result)


@click.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Show current tmux status."""
    _execute_manager_command(ctx, 'list_windows')