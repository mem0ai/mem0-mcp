"""
Pytest configuration file for mem0-mcp tests.

This file contains fixtures and mocks used across the test suite.
"""
import json
import pytest
from unittest.mock import MagicMock, patch

class MockMemoryClient:
    """Mock implementation of the MemoryClient from mem0."""
    
    def __init__(self):
        self.memories = {}
        self.next_id = 1
    
    def update_project(self, custom_instructions=None):
        """Mock method for updating project instructions."""
        self.custom_instructions = custom_instructions
        return {"status": "success"}
    
    def add(self, messages, user_id, output_format=None, metadata=None):
        """Mock method for adding a memory."""
        memory_id = f"memory_{self.next_id}"
        self.next_id += 1
        
        memory_data = {
            "id": memory_id,
            "messages": messages,
            "user_id": user_id,
            "metadata": metadata or {},
            "created_at": "2023-01-01T00:00:00Z"
        }
        
        # Store memory by user_id and project
        user_memories = self.memories.setdefault(user_id, {})
        project = metadata.get("project", "default_project") if metadata else "default_project"
        project_memories = user_memories.setdefault(project, [])
        project_memories.append(memory_data)
        
        return {"id": memory_id, "status": "success"}
    
    def get_all(self, user_id=None, page=1, page_size=10, filters=None, version=None, metadata_filters=None):
        """Mock method for retrieving all memories.
        
        Supports both v1 (deprecated) with metadata_filters and v2 with filters parameter.
        """
        user_memories = self.memories.get(user_id, {})
        results = []
        
        # Extract project from filters (v2) or metadata_filters (v1)
        project = None
        
        # Handle v2 API format
        if version == "v2" and filters and "metadata" in filters and "project" in filters["metadata"]:
            project = filters["metadata"]["project"]
        # Handle legacy v1 format for backward compatibility with tests
        elif metadata_filters and "project" in metadata_filters:
            project = metadata_filters["project"]
        
        if project:
            memories = user_memories.get(project, [])
        else:
            # Flatten all project memories
            memories = []
            for project_memories in user_memories.values():
                memories.extend(project_memories)
        
        # Apply paging
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_memories = memories[start_idx:end_idx]
        
        # Format response based on version
        if version == "v2":
            # In v2, we return memories directly
            return page_memories
        else:
            # In v1, we wrap memories in a results object
            for memory in page_memories:
                results.append({
                    "id": memory["id"],
                    "memory": {
                        "id": memory["id"],
                        "messages": memory["messages"],
                        "created_at": memory["created_at"],
                        "metadata": memory["metadata"]
                    }
                })
            
            return {
                "results": results,
                "total": len(memories),
                "page": page,
                "page_size": page_size
            }
    
    def search(self, query, user_id=None, output_format=None, filters=None, version=None, metadata_filters=None):
        """Mock method for semantic search of memories.
        
        Supports both v1 (deprecated) with metadata_filters and v2 with filters parameter.
        """
        # In our mock, we'll do a simple substring search instead of semantic search
        user_memories = self.memories.get(user_id, {})
        results = []
        
        # Extract project from filters (v2) or metadata_filters (v1)
        project = None
        
        # Handle v2 API format
        if version == "v2" and filters and "metadata" in filters and "project" in filters["metadata"]:
            project = filters["metadata"]["project"]
        # Handle legacy v1 format for backward compatibility with tests
        elif metadata_filters and "project" in metadata_filters:
            project = metadata_filters["project"]
        
        # If project filter is provided, only search within that project
        if project:
            projects_to_search = [project]
        else:
            projects_to_search = user_memories.keys()
        
        for project in projects_to_search:
            project_memories = user_memories.get(project, [])
            for memory in project_memories:
                # Simple substring search in message content
                for message in memory["messages"]:
                    if query.lower() in message.get("content", "").lower():
                        memory_result = {
                            "id": memory["id"],
                            "messages": memory["messages"],
                            "created_at": memory["created_at"],
                            "metadata": memory["metadata"],
                            "score": 0.9  # Mock score
                        }
                        
                        # For v1 format, wrap in memory object
                        if version != "v2":
                            results.append({
                                "id": memory["id"],
                                "memory": memory_result,
                                "score": 0.9
                            })
                        else:
                            # For v2, return memory directly
                            results.append(memory_result)
                        break  # Only add each memory once
        
        # Format response based on version
        if version == "v2":
            # In v2, we return an object with results array
            return {
                "results": results[:10],  # Limit to 10 results like a typical search
                "query": query
            }
        else:
            # In v1, same structure but different content
            return {
                "results": results[:10],
                "query": query
            }

@pytest.fixture
def mock_mem0_client():
    """Fixture that provides a mock Mem0 client for testing."""
    return MockMemoryClient()

@pytest.fixture
def patched_mem0_client(mock_mem0_client):
    """Fixture that patches the MemoryClient in the main module with our mock."""
    with patch("main_metadata_tagging.mem0_client", mock_mem0_client):
        yield mock_mem0_client 