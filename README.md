# Mem0 MCP Server

[![smithery badge](https://smithery.ai/badge/@mem0ai/mem0-memory-mcp)](https://smithery.ai/server/@mem0ai/mem0-memory-mcp) [![PyPI version](https://img.shields.io/pypi/v/mem0-mcp-server.svg)](https://pypi.org/project/mem0-mcp-server/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

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

## Ways to Run

You can run this server in three modes depending on your setup:

- **Local Stdio (Recommended)**: Best for Claude Desktop, Cursor, or local development. No server port management needed.
- **Smithery**: Best for deploying as a hosted HTTP endpoint or using the Smithery platform.
- **Docker**: Best for containerized deployments where you need an HTTP endpoint.

## How to Connect

### Claude Desktop & Cursor (Stdio)

The easiest way to use Mem0 is by letting `uvx` handle the installation. Add this configuration to your `claude_desktop_config.json` or Cursor MCP settings:

```json
{
  "mcpServers": {
    "mem0": {
      "command": "uvx",
      "args": ["mem0-mcp-server"],
      "env": {
        "MEM0_API_KEY": "sk_mem0_...",
        "MEM0_DEFAULT_USER_ID": "your-handle"
      }
    }
  }
}
```

### Manual Installation (CLI)

If you prefer installing the package yourself:

```bash
pip install mem0-mcp-server
```

Then run it directly:

```bash
export MEM0_API_KEY="sk_mem0_..."
mem0-mcp-server
```

## Agent Example

This repository includes a standalone agent (powered by Pydantic AI) to test the server interactively.

```bash
# Clone repo & install deps
git clone https://github.com/mem0-ai/mem0-mcp-server.git
cd mem0-mcp-server
pip install -e ".[smithery]"

# Run the agent REPL
export MEM0_API_KEY="sk_mem0_..."
export OPENAI_API_KEY="sk-openai-..."
python example/pydantic_ai_repl.py
```

This launches "Mem0Guide". Try prompts like "search memories for favorite food" to test your API key and memory storage.

## Configuration

### Environment Variables

- `MEM0_API_KEY` (required) – Mem0 platform API key.
- `MEM0_DEFAULT_USER_ID` (optional) – default `user_id` injected into filters and write requests (defaults to `mem0-mcp`).
- `MEM0_MCP_AGENT_MODEL` (optional) – default LLM for the bundled agent example.

### Config Files

For advanced usage (like switching the agent example to use Docker), this repo includes standard MCP config files in the `example/` directory:

- `example/config.json`: Local Stdio (default)
- `example/docker-config.json`: Docker HTTP

Switch configurations for the agent REPL by setting `MEM0_MCP_CONFIG_PATH`.

## Detailed Setup Guides

<details>
<summary><strong>Click to expand: Smithery, Docker, and Troubleshooting</strong></summary>

### 1. Smithery HTTP

To run the HTTP transport with Smithery:

1.  `pip install -e ".[smithery]"` (or `pip install "mem0-mcp-server[smithery]"`).
2.  Ensure `MEM0_API_KEY` (and optional `MEM0_DEFAULT_USER_ID`) are exported.
3.  `uv run smithery dev` for a local endpoint (`http://127.0.0.1:8081/mcp`).
4.  Optional: `uv run smithery playground` to open an ngrok tunnel + Smithery web UI.
5.  **Testing**: Create a config copying `example/config.json` but changing the entry to `{ "type": "http", "url": "http://127.0.0.1:8081/mcp" }`, then point `MEM0_MCP_CONFIG_PATH` to it before running the agent REPL.
6.  **Hosted deploy**: Push to GitHub, connect at [smithery.ai](https://smithery.ai/new), click Deploy.

### 2. Docker HTTP

To containerize the server:

1.  Build the image:
    ```bash
    docker build -t mem0-mcp-server .
    ```
2.  Run the container (ensure env vars are passed):
    ```bash
    docker run --rm -e MEM0_API_KEY=sk_mem0_... -p 8081:8081 mem0-mcp-server
    ```
3.  Connect clients using `example/docker-config.json`:
    ```bash
    export MEM0_MCP_CONFIG_PATH="$PWD/example/docker-config.json"
    python example/pydantic_ai_repl.py
    ```

**Troubleshooting Docker:**

- The container must be running **before** HTTP clients connect.
- Ensure `MEM0_API_KEY` is passed via `-e`.
- If clients can't connect, check that port 8081 is forwarded correctly (`-p 8081:8081`) and that the config URL is reachable.

### 3. FAQ / Troubleshooting

- **`RuntimeWarning: 'mem0_mcp_server.server' found in sys.modules…`**: Harmless warning when running the Pydantic AI REPL.
- **`session_config not found in request scope`**: Expected when running outside Smithery; the server falls back to environment variables.
- **Smithery CLI "server reference not found"**: Ensure `[tool.smithery] server = "mem0_mcp_server.server:create_server"` is present in `pyproject.toml`.

</details>

## Development

```bash
uv sync --python 3.11                  # optional, installs dev extras and lockfile
uv run --from . mem0-mcp-server        # run local checkout via uvx
```

## License

MIT