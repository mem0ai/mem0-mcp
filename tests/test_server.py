"""Tests for mem0-mcp-server core functionality."""

import pytest
from unittest.mock import Mock, patch
from src.mem0_mcp_server.server import (
    _mem0_client,
    _with_default_filters,
    _default_enable_graph,
)


class TestAPIKeyValidation:
    """Test API key validation."""

    def test_valid_api_key(self):
        """Valid API key should create client."""
        with patch("src.mem0_mcp_server.server.MemoryClient") as mock_client:
            _mem0_client("m0-valid-key-12345")
            mock_client.assert_called_once_with(api_key="m0-valid-key-12345")

    def test_invalid_api_key_prefix(self):
        """Invalid prefix should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid MEM0_API_KEY format"):
            _mem0_client("invalid-key")

    def test_invalid_api_key_length(self):
        """Too short API key should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid MEM0_API_KEY format"):
            _mem0_client("m0-short")


class TestDefaultFilters:
    """Test default filter injection."""

    def test_empty_filters(self):
        """Empty filters should add default user_id."""
        result = _with_default_filters("test-user", None)
        assert result == {"AND": [{"user_id": "test-user"}]}

    def test_simple_filter(self):
        """Simple filter should be wrapped in AND with user_id."""
        result = _with_default_filters("test-user", {"status": "active"})
        assert result == {"AND": [{"user_id": "test-user"}, {"status": "active"}]}

    def test_existing_user_id(self):
        """Existing user_id should not be duplicated."""
        filters = {"AND": [{"user_id": "other-user"}]}
        result = _with_default_filters("test-user", filters)
        assert result == {"AND": [{"user_id": "other-user"}]}

    def test_complex_filter(self):
        """Complex filter should preserve structure."""
        filters = {"OR": [{"status": "active"}, {"status": "pending"}]}
        result = _with_default_filters("test-user", filters)
        assert "user_id" in str(result)


class TestEnableGraph:
    """Test enable_graph default logic."""

    def test_explicit_true(self):
        """Explicit True should override default."""
        assert _default_enable_graph(True, False) is True

    def test_explicit_false(self):
        """Explicit False should override default."""
        assert _default_enable_graph(False, True) is False

    def test_none_uses_default(self):
        """None should use default value."""
        assert _default_enable_graph(None, True) is True
        assert _default_enable_graph(None, False) is False


class TestCacheLRU:
    """Test LRU cache behavior."""

    def test_cache_reuses_client(self):
        """Same API key should reuse cached client."""
        with patch("src.mem0_mcp_server.server.MemoryClient") as mock_client:
            _mem0_client.cache_clear()
            
            _mem0_client("m0-test-key-123")
            _mem0_client("m0-test-key-123")
            
            # Should only create client once
            assert mock_client.call_count == 1

    def test_cache_different_keys(self):
        """Different API keys should create different clients."""
        with patch("src.mem0_mcp_server.server.MemoryClient") as mock_client:
            _mem0_client.cache_clear()
            
            _mem0_client("m0-key-one-123")
            _mem0_client("m0-key-two-456")
            
            # Should create two clients
            assert mock_client.call_count == 2
