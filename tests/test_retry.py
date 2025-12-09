"""Tests for retry logic with exponential backoff."""

import json
import pytest
from unittest.mock import Mock, patch
from mem0.exceptions import MemoryError
from src.mem0_mcp_server.server import _mem0_call


class TestRetryLogic:
    """Test retry logic with exponential backoff."""

    def test_success_first_attempt(self):
        """Successful call on first attempt should not retry."""
        mock_func = Mock(return_value={"result": "success"})
        
        result = _mem0_call(mock_func)
        
        assert mock_func.call_count == 1
        assert json.loads(result) == {"result": "success"}

    def test_retry_on_5xx_error(self):
        """5xx errors should trigger retry."""
        mock_func = Mock()
        error = MemoryError("Server error")
        error.status = 500
        mock_func.side_effect = [error, error, {"result": "success"}]
        
        with patch("src.mem0_mcp_server.server.time.sleep"):
            result = _mem0_call(mock_func)
        
        assert mock_func.call_count == 3
        assert json.loads(result) == {"result": "success"}

    def test_no_retry_on_4xx_error(self):
        """4xx errors should not retry."""
        mock_func = Mock()
        error = MemoryError("Bad request")
        error.status = 400
        mock_func.side_effect = error
        
        result = _mem0_call(mock_func)
        
        assert mock_func.call_count == 1
        result_data = json.loads(result)
        assert "error" in result_data
        assert result_data["status"] == 400

    def test_max_retries_exceeded(self):
        """Should stop after max retries."""
        mock_func = Mock()
        error = MemoryError("Server error")
        error.status = 503
        mock_func.side_effect = error
        
        with patch("src.mem0_mcp_server.server.time.sleep"):
            result = _mem0_call(mock_func)
        
        assert mock_func.call_count == 3
        result_data = json.loads(result)
        assert "error" in result_data

    def test_exponential_backoff_delays(self):
        """Should use exponential backoff delays."""
        mock_func = Mock()
        error = MemoryError("Server error")
        error.status = 500
        mock_func.side_effect = error
        
        with patch("src.mem0_mcp_server.server.time.sleep") as mock_sleep:
            _mem0_call(mock_func)
        
        # Should sleep with delays: 1s, 2s
        assert mock_sleep.call_count == 2
        delays = [call[0][0] for call in mock_sleep.call_args_list]
        assert delays == [1.0, 2.0]
