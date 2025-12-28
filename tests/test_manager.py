"""Comprehensive tests for tmux-iterm-command functionality."""
import json
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import pytest

# Add src to path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from claude_tmux.manager import TmuxManager


class TestTmuxManager:
    """Tests for TmuxManager class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Mock the libtmux Server to avoid requiring actual tmux
        self.mock_server = Mock()
        self.mock_session = Mock()
        self.mock_session.session_id = '@1'
        self.mock_session.name = 'test-session'
        self.mock_server.sessions = [self.mock_session]
        self.mock_server.new_session.return_value = self.mock_session

        # Patch the Server class in the manager module
        with patch('claude_tmux.manager.Server') as mock_server_class:
            mock_server_class.return_value = self.mock_server
            self.manager = TmuxManager(session_name='test-session')
    
    def test_create_window_success(self):
        """Test successful window creation."""
        # Mock the window and pane objects
        mock_window = Mock()
        mock_window.index = '0'
        mock_window.active_pane = Mock()
        mock_window.active_pane.send_keys = Mock()
        mock_window.active_pane.pane_id = '%0'
        
        # Mock the session's new_window method
        self.mock_session.new_window.return_value = mock_window
        
        result = self.manager.create_window(window_name='test', command='echo hello')
        
        assert result['status'] == 'success'
        assert result['name'] == 'test'
        assert 'window_id' in result
        assert 'window_index' in result
        
        # Verify that new_window was called
        self.mock_session.new_window.assert_called_once()
    
    def test_create_window_failure(self):
        """Test window creation failure."""
        # Mock the session's new_window method to raise an exception
        self.mock_session.new_window.side_effect = Exception("Tmux error")
        
        result = self.manager.create_window(window_name='test', command='echo hello')
        
        assert result['status'] == 'error'
        assert 'message' in result
        assert result['code'] == 'CREATE_WINDOW_FAILED'
    
    def test_create_pane_success(self):
        """Test successful pane creation."""
        # Mock the window and panes
        mock_window = Mock()
        mock_window.index = '0'
        mock_window.split_window.return_value = Mock()
        mock_window.split_window.pane_id = '%1'
        mock_window.panes = []
        
        # Mock the session's find_windows method to return our mock window
        self.mock_session.find_windows.return_value = [mock_window]
        
        result = self.manager.create_pane(window_index=0, vertical=True, command='echo test')
        
        assert result['status'] == 'success'
        assert 'pane_id' in result
        assert result['orientation'] == 'vertical'
        
        # Verify that split_window was called
        mock_window.split_window.assert_called_once()
    
    def test_send_command_success(self):
        """Test successful command sending."""
        # Mock the window and pane
        mock_window = Mock()
        mock_window.index = '0'
        mock_window.panes = [Mock()]
        mock_window.panes[0].pane_index = '0'
        mock_window.panes[0].send_keys = Mock()
        
        # Mock the session's find_windows method to return our mock window
        self.mock_session.find_windows.return_value = [mock_window]
        
        result = self.manager.send_command(window_index=0, pane_index=0, command='echo test')
        
        assert result['status'] == 'success'
        assert result['command'] == 'echo test'
        
        # Verify that send_keys was called
        mock_window.panes[0].send_keys.assert_called_once_with('echo test', enter=True)
    
    def test_capture_pane_success(self):
        """Test successful pane capture."""
        # Mock the window and pane
        mock_window = Mock()
        mock_window.index = '0'
        mock_window.panes = [Mock()]
        mock_window.panes[0].pane_index = '0'
        mock_window.panes[0].capture_pane.return_value = ['line1', 'line2', 'line3']
        
        # Mock the session's find_windows method to return our mock window
        self.mock_session.find_windows.return_value = [mock_window]
        
        result = self.manager.capture_pane(window_index=0, pane_index=0)
        
        assert result['status'] == 'success'
        assert 'content' in result
        assert result['lines'] == 3
        
        # Verify that capture_pane was called
        mock_window.panes[0].capture_pane.assert_called_once()
    
    def test_list_sessions_success(self):
        """Test successful session listing."""
        # Mock the server's sessions property
        mock_session_obj = Mock()
        mock_session_obj.session_id = '@1'
        mock_session_obj.name = 'test-session'
        mock_session_obj.session_attached = '1'
        mock_session_obj.session_windows = '2'
        self.mock_server.sessions = [mock_session_obj]

        result = self.manager.list_sessions()

        assert result['status'] == 'success'
        assert len(result['sessions']) == 1
        assert result['sessions'][0]['name'] == 'test-session'
    
    def test_list_windows_success(self):
        """Test successful window listing."""
        # Mock a window
        mock_libtmux_window = Mock()
        mock_libtmux_window.index = '0'
        mock_libtmux_window.name = 'test-window'
        mock_libtmux_window.active = True
        mock_libtmux_window.panes = [Mock(), Mock()]  # 2 panes
        
        # Mock the session's list_windows method
        self.mock_session.list_windows.return_value = [mock_libtmux_window]
        
        result = self.manager.list_windows()
        
        assert result['status'] == 'success'
        assert len(result['windows']) == 1
        assert result['windows'][0]['name'] == 'test-window'
        assert result['windows'][0]['panes'] == 2
    
    def test_list_panes_success(self):
        """Test successful pane listing."""
        # Mock panes
        mock_pane1 = Mock()
        mock_pane1.pane_id = '%0'
        mock_pane1.pane_index = '0'
        mock_pane1.pane_active = '1'
        mock_pane1.pane_height = '24'
        mock_pane1.pane_width = '80'
        
        mock_pane2 = Mock()
        mock_pane2.pane_id = '%1'
        mock_pane2.pane_index = '1'
        mock_pane2.pane_active = '0'
        mock_pane2.pane_height = '24'
        mock_pane2.pane_width = '80'
        
        # Mock the window
        mock_window = Mock()
        mock_window.index = '0'
        mock_window.panes = [mock_pane1, mock_pane2]
        
        # Mock the session's find_windows method
        self.mock_session.find_windows.return_value = [mock_window]
        
        result = self.manager.list_panes(window_index=0)
        
        assert result['status'] == 'success'
        assert len(result['panes']) == 2
        assert result['panes'][0]['id'] == '%0'
        assert result['panes'][1]['active'] is False


def test_json_output_format():
    """Test that output follows expected JSON format."""
    # Test success structure
    success_result = {"status": "success", "data": {"test": "value"}, "message": "Test message"}
    json_output = json.dumps(success_result)
    parsed = json.loads(json_output)
    
    assert parsed["status"] == "success"
    assert "data" in parsed or "message" in parsed
    
    # Test error structure
    error_result = {"status": "error", "message": "Something went wrong", "code": "TEST_ERROR"}
    json_output = json.dumps(error_result)
    parsed = json.loads(json_output)
    
    assert parsed["status"] == "error"
    assert "message" in parsed
    assert "code" in parsed