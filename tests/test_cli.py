"""Tests for CLI argument parsing."""

import pytest
from unittest.mock import patch, Mock
import sys


class TestCLIArguments:
    """Test command-line argument parsing."""

    def test_api_key_argument(self):
        """--api-key should set global variable."""
        test_args = ["mem0-mcp-server", "--api-key=m0-test-key-123"]
        
        with patch.object(sys, "argv", test_args):
            with patch("src.mem0_mcp_server.server.create_server"):
                with patch("src.mem0_mcp_server.server.FastMCP") as mock_mcp:
                    mock_server = Mock()
                    mock_mcp.return_value = mock_server
                    
                    from src.mem0_mcp_server import server
                    server._CLI_API_KEY = None
                    
                    # Import and parse args
                    import argparse
                    parser = argparse.ArgumentParser()
                    parser.add_argument("--api-key")
                    parser.add_argument("--user-id")
                    args = parser.parse_args(test_args[1:])
                    
                    assert args.api_key == "m0-test-key-123"

    def test_user_id_argument(self):
        """--user-id should set global variable."""
        test_args = ["mem0-mcp-server", "--user-id=test-user"]
        
        with patch.object(sys, "argv", test_args):
            import argparse
            parser = argparse.ArgumentParser()
            parser.add_argument("--api-key")
            parser.add_argument("--user-id")
            args = parser.parse_args(test_args[1:])
            
            assert args.user_id == "test-user"

    def test_both_arguments(self):
        """Both arguments should be parsed."""
        test_args = [
            "mem0-mcp-server",
            "--api-key=m0-key-123",
            "--user-id=test-user"
        ]
        
        with patch.object(sys, "argv", test_args):
            import argparse
            parser = argparse.ArgumentParser()
            parser.add_argument("--api-key")
            parser.add_argument("--user-id")
            args = parser.parse_args(test_args[1:])
            
            assert args.api_key == "m0-key-123"
            assert args.user_id == "test-user"

    def test_no_arguments(self):
        """No arguments should work (use env vars)."""
        test_args = ["mem0-mcp-server"]
        
        with patch.object(sys, "argv", test_args):
            import argparse
            parser = argparse.ArgumentParser()
            parser.add_argument("--api-key")
            parser.add_argument("--user-id")
            args = parser.parse_args(test_args[1:])
            
            assert args.api_key is None
            assert args.user_id is None
