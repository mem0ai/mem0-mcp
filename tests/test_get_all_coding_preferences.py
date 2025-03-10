"""
Tests for the get_all_coding_preferences function in main_metadata_tagging.py.
"""
import pytest
import json
import sys
import os
from unittest.mock import patch

# Add the parent directory to the path so we can import the main module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main_metadata_tagging

class TestGetAllCodingPreferences:
    """Tests for the get_all_coding_preferences function."""
    
    @pytest.mark.asyncio
    async def test_get_all_empty_project(self, patched_mem0_client):
        """Test retrieving preferences when a project has no memories."""
        # Call the function with a project that doesn't exist yet
        result = await main_metadata_tagging.get_all_coding_preferences("empty_project")
        
        # Parse the JSON result
        memories = json.loads(result)
        
        # Verify an empty list is returned
        assert isinstance(memories, list)
        assert len(memories) == 0
    
    @pytest.mark.asyncio
    async def test_get_all_with_memories(self, patched_mem0_client):
        """Test retrieving preferences when a project has memories."""
        # Set up test data
        test_project = "populated_project"
        test_codes = [
            "def function1(): return 'Test 1'",
            "def function2(): return 'Test 2'",
            "def function3(): return 'Test 3'"
        ]
        
        # Add test memories to the project
        for test_code in test_codes:
            await main_metadata_tagging.add_coding_preference(test_code, test_project)
        
        # Call the function
        result = await main_metadata_tagging.get_all_coding_preferences(test_project)
        
        # Parse the JSON result
        memories = json.loads(result)
        
        # Verify the correct number of memories is returned
        assert isinstance(memories, list)
        assert len(memories) == len(test_codes)
        
        # Verify the memory content
        message_contents = [memory["messages"][0]["content"] for memory in memories]
        for test_code in test_codes:
            assert test_code in message_contents
    
    @pytest.mark.asyncio
    async def test_get_all_default_project(self, patched_mem0_client):
        """Test retrieving preferences from the default project."""
        # Add test memories to the default project
        test_code = "print('Default project test')"
        await main_metadata_tagging.add_coding_preference(test_code)
        
        # Call the function without specifying a project
        result = await main_metadata_tagging.get_all_coding_preferences()
        
        # Parse the JSON result
        memories = json.loads(result)
        
        # Verify the memory is returned
        assert isinstance(memories, list)
        assert len(memories) == 1
        assert memories[0]["messages"][0]["content"] == test_code
    
    @pytest.mark.asyncio
    async def test_get_all_project_isolation(self, patched_mem0_client):
        """Test that memories from different projects are isolated."""
        # Add memories to two different projects
        project1 = "project1"
        project2 = "project2"
        
        await main_metadata_tagging.add_coding_preference("Project 1 Code", project1)
        await main_metadata_tagging.add_coding_preference("Project 2 Code", project2)
        
        # Get memories from project1
        result = await main_metadata_tagging.get_all_coding_preferences(project1)
        memories = json.loads(result)
        
        # Verify only project1 memories are returned
        assert len(memories) == 1
        assert memories[0]["messages"][0]["content"] == "Project 1 Code"
    
    @pytest.mark.asyncio
    async def test_get_all_error_handling(self):
        """Test error handling when the client raises an exception."""
        # Patch the mem0_client.get_all method to raise an exception
        with patch("main_metadata_tagging.mem0_client.get_all", side_effect=Exception("Test error")):
            # Call the function
            result = await main_metadata_tagging.get_all_coding_preferences("test_project")
            
            # Verify error is handled properly
            assert "Error getting preferences" in result
            assert "Test error" in result 