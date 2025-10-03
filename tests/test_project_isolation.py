"""
Project Isolation Test for Mem0 API.

This script specifically tests that the get_all and search API calls only return data
for the specified project, ensuring proper isolation between different projects.
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

def run_isolation_test(verbose=False):
    """Run a test specifically focused on project isolation."""
    print("Starting Project Isolation Test")
    print("==============================\n")
    
    # Initialize the real Mem0 client
    mem0_client = MemoryClient()
    
    # Test user ID - use a specific one for this test to avoid interference
    user_id = "isolation_test_user"
    
    # Create two unique project names for testing
    project1 = f"project1_{int(time.time())}"
    project2 = f"project2_{int(time.time())}"
    
    print(f"Using test projects: '{project1}' and '{project2}'")
    
    try:
        # Step 1: Add distinct test memories to both projects
        print("\nAdding test memories to both projects...")
        
        # Add memory to project1
        code1 = '''
        def project1_function():
            """This function belongs ONLY to project1"""
            return "Project 1 function"
        '''
        messages1 = [{"role": "user", "content": code1}]
        mem0_client.add(messages1, user_id=user_id, output_format="v1.1", metadata={"project": project1})
        
        # Add memory to project2
        code2 = '''
        def project2_function():
            """This function belongs ONLY to project2"""
            return "Project 2 function"
        '''
        messages2 = [{"role": "user", "content": code2}]
        mem0_client.add(messages2, user_id=user_id, output_format="v1.1", metadata={"project": project2})
        
        print("Added one memory to each project")
        print("Waiting for memories to be indexed...")
        time.sleep(3)  # Give more time for indexing
        
        # Step 2: Test get_all for project1
        print("\nTesting get_all for project1...")
        memories1 = mem0_client.get_all(
            user_id=user_id,
            filters={"metadata": {"project": project1}},
            version="v2"
        )
        
        if verbose:
            print(f"Project1 memories: {json.dumps(memories1, indent=2)}")
        
        # Step 3: Test get_all for project2
        print("Testing get_all for project2...")
        memories2 = mem0_client.get_all(
            user_id=user_id,
            filters={"metadata": {"project": project2}},
            version="v2"
        )
        
        if verbose:
            print(f"Project2 memories: {json.dumps(memories2, indent=2)}")
        
        # Step 4: Verify isolation for get_all
        print("\nVerifying isolation for get_all...")
        
        # Function to check if a memory contains a specific text
        def contains_text(memory, text):
            if isinstance(memory, dict):
                # Check memory content
                if "memory" in memory and isinstance(memory["memory"], str) and text in memory["memory"]:
                    return True
                # Check messages if available
                if "messages" in memory:
                    for msg in memory["messages"]:
                        if "content" in msg and text in msg["content"]:
                            return True
            return False
        
        # Check that project1 memories only contain project1 content
        project1_isolation = True
        for memory in memories1:
            if contains_text(memory, "project2_function"):
                project1_isolation = False
                break
        
        # Check that project2 memories only contain project2 content
        project2_isolation = True
        for memory in memories2:
            if contains_text(memory, "project1_function"):
                project2_isolation = False
                break
        
        if project1_isolation and project2_isolation:
            print("✅ get_all API correctly maintains project isolation")
        else:
            print("❌ get_all API does NOT maintain project isolation")
            
        # Step 5: Test search for both projects with the same query
        print("\nTesting search for both projects with the same query...")
        
        # Search for "function" in project1
        search_query = "function"
        search_result1 = mem0_client.search(
            search_query,
            user_id=user_id,
            filters={"metadata": {"project": project1}},
            version="v2"
        )
        
        # Search for "function" in project2
        search_result2 = mem0_client.search(
            search_query,
            user_id=user_id,
            filters={"metadata": {"project": project2}},
            version="v2"
        )
        
        if verbose:
            print(f"\nProject1 search results: {json.dumps(search_result1, indent=2)}")
            print(f"\nProject2 search results: {json.dumps(search_result2, indent=2)}")
        
        # Extract results from response
        results1 = search_result1["results"] if isinstance(search_result1, dict) and "results" in search_result1 else search_result1
        results2 = search_result2["results"] if isinstance(search_result2, dict) and "results" in search_result2 else search_result2
        
        # Step 6: Verify search isolation
        print("\nVerifying isolation for search...")
        
        # Check that project1 search results only contain project1 content
        search1_isolation = True
        for result in results1:
            if contains_text(result, "project2_function"):
                search1_isolation = False
                break
        
        # Check that project2 search results only contain project2 content
        search2_isolation = True
        for result in results2:
            if contains_text(result, "project1_function"):
                search2_isolation = False
                break
        
        if search1_isolation and search2_isolation:
            print("✅ search API correctly maintains project isolation")
        else:
            print("❌ search API does NOT maintain project isolation")
        
        # Final results
        if project1_isolation and project2_isolation and search1_isolation and search2_isolation:
            print("\n✅ PASSED: Both get_all and search APIs correctly maintain project isolation")
            return True
        else:
            print("\n❌ FAILED: Project isolation issues detected")
            return False
            
    except Exception as e:
        print(f"\n❌ Error during isolation test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test project isolation in Mem0 API')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed API responses')
    args = parser.parse_args()
    
    success = run_isolation_test(verbose=args.verbose)
    sys.exit(0 if success else 1) 