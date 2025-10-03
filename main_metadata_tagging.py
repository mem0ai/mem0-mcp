"""
MCP Server for Mem0 Code Preferences with Metadata Tagging

This module implements a Model Control Protocol (MCP) server that integrates with the Mem0 memory system
to store, retrieve, and search coding preferences, snippets, and implementation patterns. It provides
tools for AI assistants to:

1. Add code snippets and programming knowledge to persistent memory with project-specific metadata tagging
2. Retrieve all stored coding preferences for a specific project
3. Perform semantic searches across stored code knowledge, filtered by project

The server exposes these capabilities through a FastMCP interface, making them available as tools
for AI assistants. Each memory is tagged with project metadata for better organization and retrieval.

The module also sets up a Starlette-based web server with Server-Sent Events (SSE) for real-time
communication with clients.

Usage:
    Run the script directly to start the server:
    ```
    python main_metadata_tagging.py --host 0.0.0.0 --port 8080
    ```
"""
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server import Server
import uvicorn
from mem0 import MemoryClient
from dotenv import load_dotenv
import json

load_dotenv()

# Initialize FastMCP server for mem0 tools
mcp = FastMCP("mem0-mcp")

# Initialize mem0 client and set default user
mem0_client = MemoryClient()
DEFAULT_USER_ID = "cursor_mcp"
CUSTOM_INSTRUCTIONS = """
Extract the Following Information:  

- Code Snippets: Save the actual code for future reference.  
- Explanation: Document a clear description of what the code does and how it works.
- Related Technical Details: Include information about the programming language, dependencies, and system specifications.  
- Key Features: Highlight the main functionalities and important aspects of the snippet.
"""
mem0_client.update_project(custom_instructions=CUSTOM_INSTRUCTIONS)

@mcp.tool(
    description="""Add a new coding preference to mem0.
    This tool stores code snippets, implementation details, and coding patterns for future reference.
    Use the 'project' parameter to tag the memory with a project identifier.
    """
)
async def add_coding_preference(text: str, project: str = "default_project") -> str:
    """Add a new coding preference to mem0 with metadata tagging for the project.

    This tool is designed to store code snippets, implementation patterns, and programming knowledge.
    When storing code, it's recommended to include:
    - Complete code with imports and dependencies
    - Language/framework information
    - Setup instructions if needed
    - Documentation and comments
    - Example usage

    Args:
        text: The content to store in memory, including code, documentation, and context
        project: The project identifier to tag the memory with
    """
    try:
        messages = [{"role": "user", "content": text}]
        # Pass metadata to tag the memory with the project name
        result = mem0_client.add(messages, user_id=DEFAULT_USER_ID, output_format="v1.1", metadata={"project": project})
        
        # Extract the memory ID from the result if available
        memory_id = None
        if isinstance(result, dict) and 'id' in result:
            memory_id = result['id']
        elif isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict) and 'id' in result[0]:
            memory_id = result[0]['id']
            
        if memory_id:
            return f"Successfully added preference with ID {memory_id} for project '{project}': {text}"
        else:
            return f"Successfully added preference for project '{project}': {text}"
    except Exception as e:
        return f"Error adding preference: {str(e)}"

@mcp.tool(
    description="""Retrieve all stored coding preferences for a given project.
    Provide the 'project' parameter to limit the results.
    Returns a JSON list of memories that have been tagged with the given project.
    """
)
async def get_all_coding_preferences(project: str = "default_project") -> str:
    """Get all coding preferences for the specified project.

    Returns a JSON formatted list of all stored preferences, including:
    - Code implementations and patterns
    - Technical documentation
    - Programming best practices
    - Setup guides and examples
    Each preference includes metadata about when it was created and its content type.
    """
    try:
        # Use proper v2 API format with filters
        memories = mem0_client.get_all(
            filters={"metadata": {"project": project}},
            user_id=DEFAULT_USER_ID,
            page=1,
            page_size=50,
            version="v2"
        )
        
        # Handle different response formats - v2 API returns a list directly
        if isinstance(memories, list):
            flattened_memories = memories
        elif isinstance(memories, dict) and "results" in memories:
            flattened_memories = memories["results"]
        else:
            flattened_memories = []
            
        return json.dumps(flattened_memories, indent=2)
    except Exception as e:
        return f"Error getting preferences: {str(e)}"

@mcp.tool(
    description="""Search through stored coding preferences using semantic search. 
    The 'project' parameter allows you to restrict the search to a specific project.
    This tool should be called for EVERY user query to find relevant code and implementation details. 
    It helps find:
    - Specific code implementations or patterns
    - Solutions to programming problems
    - Best practices and coding standards
    - Setup and configuration guides
    - Technical documentation and examples
    The search uses natural language understanding to find relevant matches, so you can
    describe what you're looking for in plain English. Always search the preferences before 
    providing answers to ensure you leverage existing knowledge."""
)
async def search_coding_preferences(query: str, project: str = "default_project") -> str:
    """Search coding preferences using semantic search, limited to a specific project.

    The search is powered by natural language understanding, allowing you to find:
    - Code implementations and patterns
    - Programming solutions and techniques
    - Technical documentation and guides
    - Best practices and standards
    Results are ranked by relevance to your query.

    Args:
        query: Search query string describing what you're looking for. Can be natural language
              or specific technical terms.
        project: The project identifier to restrict the search to
    """
    try:
        # Use proper v2 API format with filters
        search_result = mem0_client.search(
            query, 
            filters={"metadata": {"project": project}},
            user_id=DEFAULT_USER_ID,
            version="v2"
        )
        
        # Handle different response formats
        if isinstance(search_result, dict) and "results" in search_result:
            flattened_memories = search_result["results"]
        elif isinstance(search_result, list):
            flattened_memories = search_result
        else:
            flattened_memories = []
            
        return json.dumps(flattened_memories, indent=2)
    except Exception as e:
        return f"Error searching preferences: {str(e)}"

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can serve the provided MCP server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,  # noqa: SLF001
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

if __name__ == "__main__":
    mcp_server = mcp._mcp_server

    import argparse
    parser = argparse.ArgumentParser(description='Run MCP SSE-based server (Metadata version)')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
    args = parser.parse_args()

    # Bind SSE request handling to MCP server
    starlette_app = create_starlette_app(mcp_server, debug=True)

    uvicorn.run(starlette_app, host=args.host, port=args.port)
