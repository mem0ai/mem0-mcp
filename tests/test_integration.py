"""
Integration tests for main_metadata_tagging.py.

These tests verify that the different functions work together properly in
realistic use cases and workflows.
"""
import pytest
import json
import sys
import os

# Add the parent directory to the path so we can import the main module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main_metadata_tagging

class TestIntegration:
    """Integration tests for the main_metadata_tagging.py functions."""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, patched_mem0_client):
        """
        Test a full workflow:
        1. Add multiple code snippets to different projects
        2. Retrieve all snippets in a project
        3. Search for specific snippets
        """
        # Step 1: Add code snippets to different projects
        python_project = "python_examples"
        javascript_project = "javascript_examples"
        
        # Python snippets
        python_snippets = [
            '''
            def fibonacci(n):
                """Calculate the nth Fibonacci number."""
                if n <= 1:
                    return n
                return fibonacci(n-1) + fibonacci(n-2)
            ''',
            '''
            def quicksort(arr):
                """Quicksort implementation."""
                if len(arr) <= 1:
                    return arr
                pivot = arr[len(arr) // 2]
                left = [x for x in arr if x < pivot]
                middle = [x for x in arr if x == pivot]
                right = [x for x in arr if x > pivot]
                return quicksort(left) + middle + quicksort(right)
            ''',
            '''
            def binary_search(arr, target):
                """Binary search implementation."""
                left, right = 0, len(arr) - 1
                while left <= right:
                    mid = (left + right) // 2
                    if arr[mid] == target:
                        return mid
                    elif arr[mid] < target:
                        left = mid + 1
                    else:
                        right = mid - 1
                return -1
            '''
        ]
        
        # JavaScript snippets
        js_snippets = [
            """
            function debounce(func, wait) {
                // Debounce implementation
                let timeout;
                return function(...args) {
                    clearTimeout(timeout);
                    timeout = setTimeout(() => func.apply(this, args), wait);
                };
            }
            """,
            """
            function throttle(func, limit) {
                // Throttle implementation
                let inThrottle;
                return function(...args) {
                    if (!inThrottle) {
                        func.apply(this, args);
                        inThrottle = true;
                        setTimeout(() => inThrottle = false, limit);
                    }
                };
            }
            """
        ]
        
        # Add all snippets
        for snippet in python_snippets:
            result = await main_metadata_tagging.add_coding_preference(snippet, python_project)
            assert "Successfully added preference" in result
        
        for snippet in js_snippets:
            result = await main_metadata_tagging.add_coding_preference(snippet, javascript_project)
            assert "Successfully added preference" in result
        
        # Step 2: Retrieve all snippets in each project
        python_result = await main_metadata_tagging.get_all_coding_preferences(python_project)
        js_result = await main_metadata_tagging.get_all_coding_preferences(javascript_project)
        
        python_memories = json.loads(python_result)
        js_memories = json.loads(js_result)
        
        # Verify the correct number of memories per project
        assert len(python_memories) == len(python_snippets)
        assert len(js_memories) == len(js_snippets)
        
        # Step 3: Search for specific code patterns
        # Search for sorting algorithms in Python project
        sort_result = await main_metadata_tagging.search_coding_preferences("quicksort", python_project)
        sort_memories = json.loads(sort_result)
        
        # Verify quicksort is found
        assert len(sort_memories) >= 1
        found_quicksort = False
        for memory in sort_memories:
            if "quicksort" in memory["messages"][0]["content"].lower():
                found_quicksort = True
                break
        assert found_quicksort
        
        # Search for event handling in JavaScript project
        event_result = await main_metadata_tagging.search_coding_preferences("throttle", javascript_project)
        event_memories = json.loads(event_result)
        
        # Verify throttle function is found
        assert len(event_memories) >= 1
        found_throttle = False
        for memory in event_memories:
            if "throttle" in memory["messages"][0]["content"].lower():
                found_throttle = True
                break
        assert found_throttle
        
        # Search for binary search across both projects
        binary_result = await main_metadata_tagging.search_coding_preferences("binary search", python_project)
        binary_memories = json.loads(binary_result)
        
        # Verify binary search is found
        assert len(binary_memories) >= 1
        found_binary = False
        for memory in binary_memories:
            if "binary_search" in memory["messages"][0]["content"]:
                found_binary = True
                break
        assert found_binary
    
    @pytest.mark.asyncio
    async def test_cross_project_search_isolation(self, patched_mem0_client):
        """Test that searches are properly isolated to the specified project."""
        # Add the same code pattern to different projects with different implementations
        project1 = "frontend"
        project2 = "backend"
        
        # Add snippet with "authentication" to project1
        frontend_auth = """
        function authenticateUser(username, password) {
            // Frontend authentication logic
            return fetch('/api/login', {
                method: 'POST',
                body: JSON.stringify({ username, password })
            }).then(response => response.json());
        }
        """
        await main_metadata_tagging.add_coding_preference(frontend_auth, project1)
        
        # Add snippet with "authentication" to project2
        backend_auth = """
        def authenticate_user(username, password):
            # Backend authentication logic
            hashed_password = hash_password(password)
            user = User.query.filter_by(username=username).first()
            if user and user.password == hashed_password:
                return generate_token(user)
            return None
        """
        await main_metadata_tagging.add_coding_preference(backend_auth, project2)
        
        # Search for "authentication" in project1
        frontend_result = await main_metadata_tagging.search_coding_preferences("authentication", project1)
        frontend_memories = json.loads(frontend_result)
        
        # Verify only frontend authentication is found
        assert len(frontend_memories) == 1
        assert "Frontend authentication" in frontend_memories[0]["messages"][0]["content"]
        
        # Search for "authentication" in project2
        backend_result = await main_metadata_tagging.search_coding_preferences("authentication", project2)
        backend_memories = json.loads(backend_result)
        
        # Verify only backend authentication is found
        assert len(backend_memories) == 1
        assert "Backend authentication" in backend_memories[0]["messages"][0]["content"] 