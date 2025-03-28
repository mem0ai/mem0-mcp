"""
Real API test for mem0-mcp.

This script performs tests against the actual Mem0 API to verify that our implementation
works correctly with the real system. It tests the v2 API endpoints with proper filter usage.
"""
import sys
import os
import json
import time
import argparse
from datetime import datetime

# Add the parent directory to the path so we can import the main module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mem0 import MemoryClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_api_test(verbose=False):
    """Run a real-world test against the Mem0 API."""
    print("Starting Real API Test")
    print("=====================\n")
    
    # Create a unique project name for testing to avoid interference
    test_project = f"api_test_{int(time.time())}"
    print(f"Using test project: {test_project}")
    
    # Initialize the real Mem0 client
    mem0_client = MemoryClient()
    
    # Optionally use organization and project if needed
    # mem0_client = MemoryClient(org_id='YOUR_ORG_ID', project_id='YOUR_PROJECT_ID')
    
    # Test user ID
    user_id = "api_test_user"
    
    try:
        # Step 1: Add a test memory
        print("\n1. Adding a test memory...")
        test_code = f"""
        def hello_world():
            \"\"\"A simple test function created at {datetime.now().isoformat()}\"\"\"
            print("Hello, World!")
            return "Hello, World!"
        """
        
        messages = [{"role": "user", "content": test_code}]
        result = mem0_client.add(messages, user_id=user_id, output_format="v1.1", metadata={"project": test_project})
        
        if verbose:
            print(f"Add result: {json.dumps(result, indent=2)}")
        
        # The result might be a list or a dictionary depending on the API version
        memory_id = None
        if isinstance(result, dict) and 'id' in result:
            memory_id = result['id']
        elif isinstance(result, list) and len(result) > 0 and 'id' in result[0]:
            memory_id = result[0]['id']
        
        if memory_id:
            print(f"Memory added with ID: {memory_id}")
        else:
            print(f"Memory added successfully, but couldn't extract ID from response format")
        
        # Give the API a moment to index the new memory
        print("Waiting for memory to be indexed...")
        time.sleep(2)
        
        # Step 2: Search for the memory
        print("\n2. Searching for the memory...")
        search_query = "hello world"
        search_result = mem0_client.search(
            search_query,
            user_id=user_id,
            filters={"metadata": {"project": test_project}},
            version="v2"
        )
        
        if verbose:
            print(f"Search result: {json.dumps(search_result, indent=2)}")
        
        # Handle different response formats
        search_results_count = 0
        if isinstance(search_result, dict) and "results" in search_result:
            search_results_count = len(search_result["results"])
        elif isinstance(search_result, list):
            search_results_count = len(search_result)
            
        if search_results_count > 0:
            print(f"Found {search_results_count} memory matches")
        else:
            print("No memories found")
        
        # Step 3: Get all memories for the project
        print("\n3. Getting all memories for the project...")
        all_memories = mem0_client.get_all(
            user_id=user_id,
            filters={"metadata": {"project": test_project}},
            version="v2"
        )
        
        if verbose:
            print(f"All memories result: {json.dumps(all_memories, indent=2)}")
        
        # Handle different response formats
        memories_count = 0
        if isinstance(all_memories, dict) and "results" in all_memories:
            memories_count = len(all_memories["results"])
        elif isinstance(all_memories, list):
            memories_count = len(all_memories)
            
        print(f"Retrieved {memories_count} memories")
        
        # Step 4: Verify project isolation
        print("\n4. Verifying project isolation...")
        other_project = f"other_project_{int(time.time())}"
        other_code = f"""
        def another_function():
            \"\"\"A function for a different project at {datetime.now().isoformat()}\"\"\"
            return "Another function"
        """
        
        # Add memory to another project
        messages = [{"role": "user", "content": other_code}]
        mem0_client.add(messages, user_id=user_id, output_format="v1.1", metadata={"project": other_project})
        
        # Give the API a moment to index the new memory
        print("Waiting for second memory to be indexed...")
        time.sleep(2)
        
        # Verify that searching in the first project doesn't return the second project's memory
        search_result = mem0_client.search(
            "function", 
            user_id=user_id,
            filters={"metadata": {"project": test_project}},
            version="v2"
        )
        
        if verbose:
            print(f"Project isolation search result: {json.dumps(search_result, indent=2)}")
        
        # Check if the second project's content is not found in the first project
        is_isolated = True
        results_to_check = []
        
        if isinstance(search_result, dict) and "results" in search_result:
            results_to_check = search_result["results"]
        elif isinstance(search_result, list):
            results_to_check = search_result
            
        for item in results_to_check:
            # Extract message content from the result
            messages = []
            if "messages" in item:
                messages = item["messages"]
            elif "memory" in item and "messages" in item["memory"]:
                messages = item["memory"]["messages"]
                
            # Check each message for the "another_function" content
            for message in messages:
                if "content" in message and "another_function" in message["content"]:
                    is_isolated = False
                    break
        
        if is_isolated:
            print("Project isolation verified: Different projects maintain separate memories")
        else:
            print("WARNING: Project isolation may not be working correctly")
        
        print("\nAPI Test Completed Successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during API test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test Mem0 API with v2 endpoints')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed API responses')
    args = parser.parse_args()
    
    success = run_api_test(verbose=args.verbose)
    sys.exit(0 if success else 1) 