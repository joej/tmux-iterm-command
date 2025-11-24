"""Main CLI entry point for ticmd."""
import click
import sys
from typing import Optional

from .manager import TmuxManager
from .commands import (
    create_session,
    create_window,
    create_pane,
    list_sessions,
    list_windows,
    list_panes,
    send_command,
    capture_pane,
    wait_idle,
    kill_session,
    kill_window,
    kill_pane,
    set_badge,
    set_mark,
    notify,
    set_tab_color,
    detect,
    status
)


@click.group()
@click.version_option(version="0.1.0")
@click.option('--session', default='claude-dev', help='Tmux session name to use')
@click.option('--verbose/--no-verbose', default=False, help='Enable verbose output')
@click.pass_context
def main(ctx: click.Context, session: str, verbose: bool):
    """Tmux and iTerm2 command tool for coding agents."""
    ctx.ensure_object(dict)
    ctx.obj['SESSION'] = session
    ctx.obj['VERBOSE'] = verbose
    ctx.obj['MANAGER'] = TmuxManager(session_name=session, verbose=verbose)


# Add all commands to the CLI
main.add_command(create_session)
main.add_command(create_window)
main.add_command(create_pane)
main.add_command(list_sessions)
main.add_command(list_windows)
main.add_command(list_panes)
main.add_command(send_command)
main.add_command(capture_pane)
main.add_command(wait_idle)
main.add_command(kill_session)
main.add_command(kill_window)
main.add_command(kill_pane)
main.add_command(set_badge)
main.add_command(set_mark)
main.add_command(notify)
main.add_command(set_tab_color)
main.add_command(detect)
main.add_command(status)


def run():
    """Run the main CLI."""
    try:
        main(obj={})
    except KeyboardInterrupt:
        click.echo("\nOperation interrupted by user.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    run()