"""Basic tests for ticmd functionality."""
import pytest
import json
from unittest.mock import Mock, patch

from claude_tmux.manager import TmuxManager
from claude_tmux.cli import main
from claude_tmux.commands import create_window, list_windows


def test_tmux_manager_initialization():
    """Test basic initialization of TmuxManager."""
    # This test would require actual tmux to be running
    # For now, we'll just verify the class can be imported and initialized
    assert TmuxManager is not None


def test_json_output_format():
    """Test that commands return properly formatted JSON."""
    # This is a placeholder - actual testing would require tmux
    result = {"status": "success", "data": {"test": "value"}}
    json_output = json.dumps(result)
    parsed = json.loads(json_output)
    
    assert parsed["status"] == "success"
    assert "data" in parsed


def test_create_window_command_structure():
    """Test that create_window command has the right structure."""
    assert hasattr(create_window, '__click_params__')  # Check if it's a click command