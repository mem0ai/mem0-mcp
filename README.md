# Mem0 MCP Server

[![PyPI version](https://img.shields.io/pypi/v/mem0-mcp-server.svg)](https://pypi.org/project/mem0-mcp-server/) [![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

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

## Installation

### Install from PyPI (Recommended)

```bash
pip install mem0-mcp-server
```

This installs the command-line tool `mem0-mcp-server` that you can use with any MCP client.

## Quick Start

### Claude Desktop & Cursor

The easiest way to use Mem0 is by adding this configuration to your `claude_desktop_config.json` or Cursor MCP settings:

```json
{
  "mcpServers": {
    "mem0": {
      "command": "mem0-mcp-server",
      "env": {
        "MEM0_API_KEY": "sk_mem0_...",
        "MEM0_DEFAULT_USER_ID": "your-handle"
      }
    }
  }
}
```

### Command Line Usage

```bash
# Set your API key
export MEM0_API_KEY="sk_mem0_..."

# Run the server
mem0-mcp-server
```

### Python Agent Example

Try the interactive Pydantic AI agent to test the server:

```bash
# Clone the repository
git clone https://github.com/mem0ai/mem0-mcp-server.git
cd mem0-mcp-server

# Install with agent dependencies
pip install -e ".[agent]"

# Set required environment variables
export MEM0_API_KEY="sk_mem0_..."
export OPENAI_API_KEY="sk-openai-..."

# Run the agent
python example/pydantic_ai_repl.py
```

This launches "Mem0Guide". Try prompts like:
- "Remember that I love pepperoni pizza"
- "What do you know about my food preferences?"
- "Search for memories about my projects"

**Using with different configurations:**

```bash
# Use local server (default)
python example/pydantic_ai_repl.py

# Use Smithery server
export MEM0_MCP_CONFIG_PATH=example/config-smithery.json
export MEM0_MCP_CONFIG_SERVER=mem0-memory-mcp
python example/pydantic_ai_repl.py

# Use Docker server
export MEM0_MCP_CONFIG_PATH=example/config-docker.json
export MEM0_MCP_CONFIG_SERVER=mem0-docker
python example/pydantic_ai_repl.py
```

## Filter Guidelines

Mem0 filters use JSON with logical operators. Key rules:

- **Don't mix entities in AND**: `{"AND": [{"user_id": "john"}, {"agent_id": "bot"}]}` is invalid
- **Use OR for different entities**: `{"OR": [{"user_id": "john"}, {"agent_id": "bot"}]}` works
- **Default user_id**: Added automatically if not specified

### Quick Examples
```json
// Single user
{"AND": [{"user_id": "john"}]}

// Agent memories only
{"AND": [{"agent_id": "schedule_bot"}]}

// Multiple users
{"AND": [{"user_id": {"in": ["john", "jane"]}}]}

// Cross-entity search
{"OR": [{"user_id": "john"}, {"agent_id": "bot"}]}

// Recent memories
{"AND": [{"user_id": "john"}, {"created_at": {"gte": "2024-01-01"}}]}
```

## Configuration

### Environment Variables

- `MEM0_API_KEY` (required) – Mem0 platform API key.
- `MEM0_DEFAULT_USER_ID` (optional) – default `user_id` injected into filters and write requests (defaults to `mem0-mcp`).
- `MEM0_MCP_AGENT_MODEL` (optional) – default LLM for the bundled agent example (defaults to `openai:gpt-4o-mini`).

## Advanced Setup

<details>
<summary><strong>Click to expand: Smithery, Docker, and Development</strong></summary>

### Smithery Deployment

To deploy on Smithery platform:

1. Install with Smithery support:
   ```bash
   pip install "mem0-mcp-server[smithery]"
   ```

2. Configure MCP client with Smithery:
   ```json
   {
     "mcpServers": {
       "mem0-memory-mcp": {
         "command": "npx",
         "args": [
           "-y", "@smithery/cli@latest",
           "run", "@mem0ai/mem0-memory-mcp",
           "--key", "your-smithery-key",
           "--profile", "your-profile-name"
         ],
         "env": {
           "MEM0_API_KEY": "sk_mem0_..."
         }
       }
     }
   }
   ```

### Docker Deployment

To run with Docker:

1. Build the image:
   ```bash
   docker build -t mem0-mcp-server .
   ```

2. Run the container:
   ```bash
   docker run --rm -e MEM0_API_KEY=sk_mem0_... -p 8081:8081 mem0-mcp-server
   ```

### Development Setup

Clone and run from source:

```bash
git clone https://github.com/mem0-ai/mem0-mcp-server.git
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

Apache License 2.0