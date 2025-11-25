"""Pytest configuration for tmux-iterm-command tests."""
import sys
import os
import pytest

# Add src to path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def mock_tmux_manager():
    """Provide a mocked TmuxManager for testing."""
    from unittest.mock import Mock, patch
    
    # Create a mock manager
    mock_manager = Mock()
    mock_manager.session_name = "test-session"
    mock_manager.verbose = False
    
    return mock_manager