"""Core TmuxManager class using libtmux for tmux operations."""
import os
import time
import base64
from typing import Dict, List, Optional, Any
from pathlib import Path

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

        # Try to get the specified session (must already exist)
        sessions = self.server.list_sessions()
        for session in sessions:
            if session.get('session_name') == session_name:
                self._session = session
                break

        # If no session found with specified name, pick the first available session
        if self._session is None and sessions:
            session = sessions[0]
            self._session = session
            self.session_name = session.get('session_name')
    
    
    @property
    def session(self) -> Session:
        """Get the current tmux session."""
        if self._session is None:
            raise RuntimeError("No tmux session available - please ensure at least one session exists")
        return self._session
    
    def create_window(self, window_name: str, command: Optional[str] = None, 
                     shell: str = "/bin/bash") -> Dict[str, Any]:
        """Create a new window in the session."""
        try:
            # Create window with shell first (to prevent output loss)
            window = self.session.new_window(
                window_name=window_name,
                attach=False,
                start_directory=None
            )
            
            # Get the pane in the new window
            pane = window.attached_pane
            if not pane:
                raise RuntimeError("No attached pane found in new window")
            
            # Launch shell first
            pane.send_keys(shell, enter=True)
            time.sleep(0.2)  # Brief pause to ensure shell starts
            
            # Send command if provided
            if command:
                pane.send_keys(command, enter=True)
            
            result = {
                "status": "success",
                "window_id": f"{self.session.session_id}:{window.index}",
                "window_index": int(window.index),
                "pane_id": pane.pane_id,
                "name": window_name,
                "session": self.session_name,
                "inside_tmux": self.inside_tmux
            }
            
            if self.verbose:
                print(f"Created window: {result}")
            
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "code": "CREATE_WINDOW_FAILED"
            }
    
    def create_pane(self, window_index: int, vertical: bool = True,
                   command: Optional[str] = None) -> Dict[str, Any]:
        """Split a window to create a new pane."""
        try:
            window = self.session.find_where({'window_index': str(window_index)})
            if not window:
                return {
                    "status": "error",
                    "message": f"Window {window_index} not found",
                    "code": "WINDOW_NOT_FOUND"
                }
            
            # Split the window to create a new pane
            split_method = 'v' if vertical else 'h'
            new_pane = window.split_window(attach=False, vertical=vertical)
            
            # Send command if provided
            if command:
                new_pane.send_keys(command, enter=True)
            
            result = {
                "status": "success",
                "pane_id": new_pane.pane_id,
                "window_index": window_index,
                "orientation": "vertical" if vertical else "horizontal",
                "session": self.session_name
            }
            
            if self.verbose:
                print(f"Created pane: {result}")
            
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "code": "CREATE_PANE_FAILED"
            }
    
    def _find_pane_by_index(self, window_index: int, pane_index: int) -> tuple:
        """Helper method to find a pane by window and pane index."""
        window = self.session.find_where({'window_index': str(window_index)})
        if not window:
            return None, None, f"Window {window_index} not found"

        for pane in window.panes:
            if pane.pane_index == str(pane_index):
                return window, pane, None

        return window, None, f"Pane {pane_index} not found in window {window_index}"

    def send_command(self, window_index: int, pane_index: int,
                    command: str, enter: bool = True) -> Dict[str, Any]:
        """Send a command to a specific pane."""
        try:
            window, target_pane, error = self._find_pane_by_index(window_index, pane_index)
            if error:
                return {
                    "status": "error",
                    "message": error,
                    "code": "PANE_NOT_FOUND"
                }

            target_pane.send_keys(command, enter=enter)

            result = {
                "status": "success",
                "command": command,
                "window_index": window_index,
                "pane_index": pane_index,
                "session": self.session_name
            }

            if self.verbose:
                print(f"Sent command: {result}")

            return result
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "code": "SEND_COMMAND_FAILED"
            }

    def capture_pane(self, window_index: int, pane_index: int,
                    lines: int = 100) -> Dict[str, Any]:
        """Capture output from a specific pane."""
        try:
            window, target_pane, error = self._find_pane_by_index(window_index, pane_index)
            if error:
                return {
                    "status": "error",
                    "message": error,
                    "code": "PANE_NOT_FOUND"
                }

            # Capture pane content
            result = target_pane.capture_pane()

            if result is None:
                result = []

            # Only return the requested number of lines from the end
            if len(result) > lines:
                result = result[-lines:]

            output = '\n'.join(result) if result else ''

            return {
                "status": "success",
                "content": output,
                "lines": len(result),
                "window_index": window_index,
                "pane_index": pane_index,
                "session": self.session_name
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "code": "CAPTURE_PANE_FAILED"
            }

    def wait_idle(self, window_index: int, pane_index: int,
                 timeout: int = 30, quiet_for: int = 2, poll_interval: float = 0.1) -> Dict[str, Any]:
        """Wait for a pane to be idle (no output for quiet_for seconds)."""
        try:
            window, target_pane, error = self._find_pane_by_index(window_index, pane_index)
            if error:
                return {
                    "status": "error",
                    "message": error,
                    "code": "PANE_NOT_FOUND"
                }

            start_time = time.time()
            last_content = ""
            last_change_time = start_time

            while time.time() - start_time < timeout:
                current_content = target_pane.capture_pane()
                if current_content is None:
                    current_content = []
                current_content_str = '\n'.join(current_content) if current_content else ''

                if current_content_str != last_content:
                    last_content = current_content_str
                    last_change_time = time.time()
                elif time.time() - last_change_time >= quiet_for:
                    elapsed = time.time() - start_time
                    return {
                        "status": "success",
                        "elapsed": elapsed,
                        "window_index": window_index,
                        "pane_index": pane_index,
                        "session": self.session_name
                    }

                time.sleep(poll_interval)  # Made configurable for efficiency optimization

            elapsed = time.time() - start_time
            return {
                "status": "timeout",
                "elapsed": elapsed,
                "timeout": timeout,
                "window_index": window_index,
                "pane_index": pane_index,
                "session": self.session_name
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "code": "WAIT_IDLE_FAILED"
            }
    
    def list_sessions(self) -> Dict[str, Any]:
        """List all tmux sessions."""
        try:
            sessions = self.server.list_sessions()
            session_list = []
            for session in sessions:
                session_info = {
                    "id": session.get('session_id'),
                    "name": session.get('session_name'),
                    "attached": session.get('session_attached') == '1',
                    "windows": int(session.get('session_windows', 0))
                }
                session_list.append(session_info)
            
            return {
                "status": "success",
                "sessions": session_list
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "code": "LIST_SESSIONS_FAILED"
            }
    
    def list_windows(self, session_name: Optional[str] = None) -> Dict[str, Any]:
        """List all windows in the session."""
        try:
            target_session = self.session if session_name is None or session_name == self.session_name else self.server.find_where({'session_name': session_name})
            if not target_session:
                return {
                    "status": "error",
                    "message": f"Session {session_name or self.session_name} not found",
                    "code": "SESSION_NOT_FOUND"
                }
            
            windows = target_session.list_windows()
            window_list = []
            for window in windows:
                window_info = {
                    "index": int(window.index),
                    "name": window.name,
                    "active": window.active,
                    "panes": len(window.panes)
                }
                window_list.append(window_info)
            
            return {
                "status": "success",
                "session": target_session.name,
                "windows": window_list
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "code": "LIST_WINDOWS_FAILED"
            }
    
    def list_panes(self, window_index: int) -> Dict[str, Any]:
        """List all panes in a specific window."""
        try:
            window = self.session.find_where({'window_index': str(window_index)})
            if not window:
                return {
                    "status": "error",
                    "message": f"Window {window_index} not found",
                    "code": "WINDOW_NOT_FOUND"
                }
            
            panes = window.panes
            pane_list = []
            for pane in panes:
                pane_info = {
                    "id": pane.pane_id,
                    "index": int(pane.pane_index),
                    "active": pane.pane_active == "1",
                    "height": int(pane.pane_height),
                    "width": int(pane.pane_width)
                }
                pane_list.append(pane_info)
            
            return {
                "status": "success",
                "window_index": window_index,
                "panes": pane_list
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "code": "LIST_PANES_FAILED"
            }

    def kill_window(self, window_index: int) -> Dict[str, Any]:
        """Kill a window in the session."""
        try:
            window = self.session.find_where({'window_index': str(window_index)})
            if not window:
                return {
                    "status": "error",
                    "message": f"Window {window_index} not found",
                    "code": "WINDOW_NOT_FOUND"
                }

            window.kill_window()
            
            return {
                "status": "success",
                "window_index": window_index,
                "session": self.session_name
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "code": "KILL_WINDOW_FAILED"
            }
    
    def kill_pane(self, window_index: int, pane_index: int) -> Dict[str, Any]:
        """Kill a pane in a specific window."""
        try:
            window = self.session.find_where({'window_index': str(window_index)})
            if not window:
                return {
                    "status": "error",
                    "message": f"Window {window_index} not found",
                    "code": "WINDOW_NOT_FOUND"
                }

            # Find the pane by index within the window
            target_pane = None
            for pane in window.panes:
                if pane.pane_index == str(pane_index):
                    target_pane = pane
                    break
            
            if not target_pane:
                return {
                    "status": "error",
                    "message": f"Pane {pane_index} not found in window {window_index}",
                    "code": "PANE_NOT_FOUND"
                }
            
            target_pane.kill_pane()
            
            return {
                "status": "success",
                "window_index": window_index,
                "pane_index": pane_index,
                "session": self.session_name
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "code": "KILL_PANE_FAILED"
            }