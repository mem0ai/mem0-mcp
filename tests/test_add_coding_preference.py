"""
Tests for the add_coding_preference function in main_metadata_tagging.py.
"""
import pytest
import json
import sys
import os
from unittest.mock import patch

# Add the parent directory to the path so we can import the main module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main_metadata_tagging

class TestAddCodingPreference:
    """Tests for the add_coding_preference function."""
    
    @pytest.mark.asyncio
    async def test_add_preference_success(self, patched_mem0_client):
        """Test that a preference can be successfully added."""
        # Set up test data
        test_code = """
        def hello_world():
            print("Hello, World!")
        """
        test_project = "test_project"
        
        # Call the function
        result = await main_metadata_tagging.add_coding_preference(test_code, test_project)
        
        # Verify results
        assert "Successfully added preference" in result
        assert test_project in result
        
        # Verify the memory was added to the mock client
        memories = patched_mem0_client.memories[main_metadata_tagging.DEFAULT_USER_ID][test_project]
        assert len(memories) == 1
        assert memories[0]["messages"][0]["content"] == test_code
        assert memories[0]["metadata"]["project"] == test_project
    
    @pytest.mark.asyncio
    async def test_add_preference_default_project(self, patched_mem0_client):
        """Test that a preference is added to the default project when no project is specified."""
        # Set up test data
        test_code = "print('Default project test')"
        
        # Call the function without specifying a project
        result = await main_metadata_tagging.add_coding_preference(test_code)
        
        # Verify results
        assert "Successfully added preference" in result
        assert "default_project" in result
        
        # Verify the memory was added to the default project
        memories = patched_mem0_client.memories[main_metadata_tagging.DEFAULT_USER_ID]["default_project"]
        assert len(memories) == 1
        assert memories[0]["messages"][0]["content"] == test_code
        assert memories[0]["metadata"]["project"] == "default_project"
    
    @pytest.mark.asyncio
    async def test_add_multiple_preferences(self, patched_mem0_client):
        """Test that multiple preferences can be added to the same project."""
        # Set up test data
        test_project = "multi_pref_project"
        test_codes = [
            "def function1(): return 'Test 1'",
            "def function2(): return 'Test 2'",
            "def function3(): return 'Test 3'"
        ]
        
        # Add multiple preferences
        for test_code in test_codes:
            result = await main_metadata_tagging.add_coding_preference(test_code, test_project)
            assert "Successfully added preference" in result
        
        # Verify all memories were added
        memories = patched_mem0_client.memories[main_metadata_tagging.DEFAULT_USER_ID][test_project]
        assert len(memories) == len(test_codes)
        
        # Verify each memory has the correct content
        for i, memory in enumerate(memories):
            assert memory["messages"][0]["content"] == test_codes[i]
            assert memory["metadata"]["project"] == test_project
    
    @pytest.mark.asyncio
    async def test_add_preference_error_handling(self):
        """Test error handling when the client raises an exception."""
        # Patch the mem0_client.add method to raise an exception
        with patch("main_metadata_tagging.mem0_client.add", side_effect=Exception("Test error")):
            # Call the function
            result = await main_metadata_tagging.add_coding_preference("Test code", "test_project")
            
            # Verify error is handled properly
            assert "Error adding preference" in result
            assert "Test error" in result 