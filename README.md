# Mem0 MCP Server

[![PyPI version](https://img.shields.io/pypi/v/mem0-mcp-server.svg)](https://pypi.org/project/mem0-mcp-server/) [![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE) [![smithery badge](https://smithery.ai/badge/@mem0ai/mem0-memory-mcp)](https://smithery.ai/server/@mem0ai/mem0-memory-mcp)

`mem0-mcp-server` wraps the official [Mem0](https://mem0.ai) Memory API as a Model Context Protocol (MCP) server so any MCP-compatible client (Claude Desktop, Cursor, custom agents) can add, search, update, and delete long-term memories.

## Tools

The server exposes the following tools to your LLM:

| Tool                  | Description                                                                       |
| --------------------- | --------------------------------------------------------------------------------- |
| `add_memory`          | Save text or conversation history (or explicit message objects) for a user/agent. |
| `search_memories`     | Semantic search across existing memories (filters + limit supported).             |
| `get_memories`        | List memories with structured filters and pagination.                             |
| `get_memory`          | Retrieve one memory by its `memory_id`.                                           |
| `update_memory`       | Overwrite a memory's text once the user confirms the `memory_id`.                 |
| `delete_memory`       | Delete a single memory by `memory_id`.                                            |
| `delete_all_memories` | Bulk delete all memories in the confirmed scope (user/agent/app/run).             |
| `delete_entities`     | Delete a user/agent/app/run entity (and its memories).                            |
| `list_entities`       | Enumerate users/agents/apps/runs stored in Mem0.                                  |

All responses are JSON strings returned directly from the Mem0 API.

## Usage Options

There are three ways to use the Mem0 MCP Server:

1. **Python Package** - Install and run locally using `uvx` with any MCP client
2. **Docker** - Containerized deployment that creates an `/mcp` HTTP endpoint
3. **Smithery** - Remote hosted service for managed deployments

## Quick Start

### Installation

```bash
uv pip install mem0-mcp-server
```

Or with pip:

```bash
pip install mem0-mcp-server
```

### Client Configuration

Add this configuration to your MCP client:

```json
{
  "mcpServers": {
    "mem0": {
      "command": "uvx",
      "args": ["mem0-mcp-server"],
      "env": {
        "MEM0_API_KEY": "m0-...",
        "MEM0_DEFAULT_USER_ID": "your-handle"
      }
    }
  }
}
```

### Test with the Python Agent

<details>
<summary><strong>Click to expand: Test with the Python Agent</strong></summary>

To test the server immediately, use the included Pydantic AI agent:

```bash
# Install the package
pip install mem0-mcp-server
# Or with uv
uv pip install mem0-mcp-server

# Set your API keys
export MEM0_API_KEY="m0-..."
export OPENAI_API_KEY="sk-openai-..."

# Clone and test with the agent
git clone https://github.com/mem0ai/mem0-mcp.git
cd mem0-mcp-server
python example/pydantic_ai_repl.py
```

**Using different server configurations:**

```bash
# Use with Docker container
export MEM0_MCP_CONFIG_PATH=example/docker-config.json
export MEM0_MCP_CONFIG_SERVER=mem0-docker
python example/pydantic_ai_repl.py

# Use with Smithery remote server
export MEM0_MCP_CONFIG_PATH=example/config-smithery.json
export MEM0_MCP_CONFIG_SERVER=mem0-memory-mcp
python example/pydantic_ai_repl.py
```

</details>

## What You Can Do

The Mem0 MCP server enables powerful memory capabilities for your AI applications:

- Remember that I'm allergic to peanuts and shellfish - Add new health information to memory
- Store these trial parameters: 200 participants, double-blind, placebo-controlled study - Save research data
- What do you know about my dietary preferences? - Search and retrieve all food-related memories
- Update my project status: the mobile app is now 80% complete - Modify existing memory with new info
- Delete all memories from 2023, I need a fresh start - Bulk remove outdated memories
- Show me everything I've saved about the Phoenix project - List all memories for a specific topic

## Configuration

### Environment Variables

- `MEM0_API_KEY` (required) – Mem0 platform API key.
- `MEM0_DEFAULT_USER_ID` (optional) – default `user_id` injected into filters and write requests (defaults to `mem0-mcp`).
- `MEM0_ENABLE_GRAPH_DEFAULT` (optional) – Enable graph memories by default (defaults to `false`).
- `MEM0_MCP_AGENT_MODEL` (optional) – default LLM for the bundled agent example (defaults to `openai:gpt-4o-mini`).

## Advanced Setup

<details>
<summary><strong>Click to expand: Docker, Smithery, and Development</strong></summary>

### Docker Deployment

To run with Docker:

1. Build the image:

   ```bash
   docker build -t mem0-mcp-server .
   ```

2. Run the container:

   ```bash
   docker run --rm -d \
     --name mem0-mcp \
     -e MEM0_API_KEY=m0-... \
     -p 8080:8081 \
     mem0-mcp-server
   ```

3. Monitor the container:

   ```bash
   # View logs
   docker logs -f mem0-mcp

   # Check status
   docker ps
   ```

### Running with Smithery Remote Server

To connect to a Smithery-hosted server:

1. Install the MCP server (Smithery dependencies are now bundled):

   ```bash
   pip install mem0-mcp-server
   ```

2. Configure MCP client with Smithery:
   ```json
   {
     "mcpServers": {
       "mem0-memory-mcp": {
         "command": "npx",
         "args": [
           "-y",
           "@smithery/cli@latest",
           "run",
           "@mem0ai/mem0-memory-mcp",
           "--key",
           "your-smithery-key",
           "--profile",
           "your-profile-name"
         ],
         "env": {
           "MEM0_API_KEY": "m0-..."
         }
       }
     }
   }
   ```

### Development Setup

Clone and run from source:

```bash
git clone https://github.com/mem0ai/mem0-mcp.git
cd mem0-mcp-server
pip install -e ".[dev]"

# Run locally
mem0-mcp-server

# Or with uv
uv sync
uv run mem0-mcp-server
```

</details>

## License

[Apache License 2.0](https://github.com/mem0ai/mem0-mcp/blob/main/LICENSE)
