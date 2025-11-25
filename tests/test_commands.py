"""Tests for CLI commands."""
import json
import sys
import os
from io import StringIO
from unittest.mock import Mock, patch
import pytest

# Add src to path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tmux_iterm_command.commands import output_result


def test_output_result_function():
    """Test that output_result function works correctly."""
    # Capture stdout
    captured_output = StringIO()
    
    test_result = {"status": "success", "data": {"test": "value"}}
    
    # Since print() goes to sys.stdout, we need to capture it differently
    import builtins
    original_print = builtins.print
    
    printed_output = []
    def mock_print(*args, **kwargs):
        printed_output.extend(args)
    
    builtins.print = mock_print
    try:
        output_result(test_result)
        # Should have printed JSON string
        assert len(printed_output) == 1
        parsed = json.loads(printed_output[0])
        assert parsed["status"] == "success"
        assert parsed["data"]["test"] == "value"
    finally:
        builtins.print = original_print


def test_command_functions_exist():
    """Test that CLI command functions exist and have expected structure."""
    import tmux_iterm_command.commands as cmd_module
    
    # Check that command functions exist
    assert hasattr(cmd_module, 'create_window')
    assert hasattr(cmd_module, 'list_windows')
    assert hasattr(cmd_module, 'send_command')
    assert hasattr(cmd_module, 'capture_pane')
    assert hasattr(cmd_module, 'kill_window')
    
    # Check that they have the expected attributes of Click commands
    assert hasattr(cmd_module.create_window, '__click_params__')
    assert hasattr(cmd_module.list_windows, '__click_params__')
    assert hasattr(cmd_module.send_command, '__click_params__')
    assert hasattr(cmd_module.capture_pane, '__click_params__')
    assert hasattr(cmd_module.kill_window, '__click_params__')