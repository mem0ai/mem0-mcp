"""
Tests for the search_coding_preferences function in main_metadata_tagging.py.
"""
import pytest
import json
import sys
import os
from unittest.mock import patch

# Add the parent directory to the path so we can import the main module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main_metadata_tagging

class TestSearchCodingPreferences:
    """Tests for the search_coding_preferences function."""
    
    @pytest.mark.asyncio
    async def test_search_empty_project(self, patched_mem0_client):
        """Test searching when a project has no memories."""
        # Call the search function on an empty project
        result = await main_metadata_tagging.search_coding_preferences("test query", "empty_project")
        
        # Parse the JSON result
        memories = json.loads(result)
        
        # Verify an empty list is returned
        assert isinstance(memories, list)
        assert len(memories) == 0
    
    @pytest.mark.asyncio
    async def test_search_with_matches(self, patched_mem0_client):
        """Test searching when there are matching memories."""
        # Set up test data
        test_project = "search_project"
        test_codes = [
            "def find_me(): return 'This should be found'",
            "def ignore_me(): return 'This should not be found'",
            "def also_find_me(): return 'This should also be found'"
        ]
        
        # Add test memories to the project
        for test_code in test_codes:
            await main_metadata_tagging.add_coding_preference(test_code, test_project)
        
        # Call the search function with a query that should match two of the memories
        result = await main_metadata_tagging.search_coding_preferences("find", test_project)
        
        # Parse the JSON result
        memories = json.loads(result)
        
        # Verify the correct number of memories is returned
        assert isinstance(memories, list)
        assert len(memories) == 2  # Should find two memories with "find" in them
        
        # Verify the memory content
        message_contents = [memory["messages"][0]["content"] for memory in memories]
        assert "def find_me(): return 'This should be found'" in message_contents
        assert "def also_find_me(): return 'This should also be found'" in message_contents
        assert "def ignore_me(): return 'This should not be found'" not in message_contents
    
    @pytest.mark.asyncio
    async def test_search_no_matches(self, patched_mem0_client):
        """Test searching when there are no matching memories."""
        # Set up test data
        test_project = "no_match_project"
        await main_metadata_tagging.add_coding_preference("def example(): pass", test_project)
        
        # Call the search function with a query that shouldn't match
        result = await main_metadata_tagging.search_coding_preferences("nonexistent", test_project)
        
        # Parse the JSON result
        memories = json.loads(result)
        
        # Verify no memories are returned
        assert isinstance(memories, list)
        assert len(memories) == 0
    
    @pytest.mark.asyncio
    async def test_search_default_project(self, patched_mem0_client):
        """Test searching in the default project."""
        # Add test memory to the default project
        test_code = "print('Default project searchable content')"
        await main_metadata_tagging.add_coding_preference(test_code)
        
        # Call the search function without specifying a project
        result = await main_metadata_tagging.search_coding_preferences("searchable")
        
        # Parse the JSON result
        memories = json.loads(result)
        
        # Verify the memory is returned
        assert isinstance(memories, list)
        assert len(memories) == 1
        assert memories[0]["messages"][0]["content"] == test_code
    
    @pytest.mark.asyncio
    async def test_search_project_isolation(self, patched_mem0_client):
        """Test that search is isolated to the specified project."""
        # Add memories to two different projects with similar content
        project1 = "search_isolation1"
        project2 = "search_isolation2"
        
        await main_metadata_tagging.add_coding_preference("Project 1 special code", project1)
        await main_metadata_tagging.add_coding_preference("Project 2 special code", project2)
        
        # Search in project1 for "special"
        result = await main_metadata_tagging.search_coding_preferences("special", project1)
        memories = json.loads(result)
        
        # Verify only project1 memories are returned
        assert len(memories) == 1
        assert memories[0]["messages"][0]["content"] == "Project 1 special code"
    
    @pytest.mark.asyncio
    async def test_search_error_handling(self):
        """Test error handling when the client raises an exception."""
        # Patch the mem0_client.search method to raise an exception
        with patch("main_metadata_tagging.mem0_client.search", side_effect=Exception("Test error")):
            # Call the function
            result = await main_metadata_tagging.search_coding_preferences("query", "test_project")
            
            # Verify error is handled properly
            assert "Error searching preferences" in result
            assert "Test error" in result 