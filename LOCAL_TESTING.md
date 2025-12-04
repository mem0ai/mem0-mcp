# Local Testing & Development Guide

This guide provides detailed instructions for developers to run, test, and debug the `mem0-mcp-server` locally. It covers three main execution modes:

1.  **Local Python Environment** (Stdio via `uv` or `pip`)
2.  **Smithery** (Hosted HTTP simulation)
3.  **Docker** (Containerized deployment)

---

## 1. Prerequisites

Before starting, ensure you have the following installed:

-   **Python 3.10+**
-   **[uv](https://docs.astral.sh/uv/)** (highly recommended) or `pip`
-   **Docker** (required for container testing)
-   **Git**

---

## 2. Initial Setup

Clone the repository and verify your environment.

```bash
git clone https://github.com/mem0-ai/mem0-mcp-server.git
cd mem0-mcp-server
```

### Install Dependencies

We recommend using `uv` to manage dependencies and virtual environments automatically.

```bash
# Sync dependencies and install the 'smithery' extra for dev tools
uv sync --extra smithery
```

If you prefer `pip`:

```bash
# Create a venv (optional but recommended)
python -m venv .venv
source .venv/bin/activate

# Install editable package with dev extras
pip install -e ".[smithery]"
```

---

## 3. Configuration

The server relies on environment variables and configuration files to know how to start and how to connect to Mem0.

### Environment Variables

You must export these variables in your shell before running any commands:

```bash
# Required: Your Mem0 API Key
export MEM0_API_KEY="sk_mem0_..."

# Optional: Default user for this server instance
export MEM0_DEFAULT_USER_ID="mem0-dev-user"

# Optional: OpenAI Key (only for running the Agent REPL example)
export OPENAI_API_KEY="sk-proj-..."
```

### Project Config Files

If you are modifying the server setup, be aware of these two key files:

1.  **`pyproject.toml`**: Defines the entry point for Smithery.
    ```toml
    [tool.smithery]
    server = "mem0_mcp_server.server:create_server"
    ```
2.  **`smithery.yaml`**: Minimal config telling Smithery this is a Python project.
    ```yaml
    runtime: "python"
    ```

---

## 4. Mode A: Local Python (Stdio)

This is the fastest way to iterate on code. The server runs directly in your terminal process.

### Running the Server

You can start the server directly to verify it boots without errors:

```bash
# Using uv (no install needed if synced)
uv run mem0-mcp-server

# Or using the installed script
mem0-mcp-server
```

*Note: The server communicates via JSON-RPC on stdio. It will appear to "hang" while waiting for input. This is normal.*

### Testing with the Agent REPL

We include a Pydantic AI agent to interactively test the server tools.

```bash
# Ensure env vars are set!
export MEM0_API_KEY="sk_mem0_..."

# Run the REPL
python example/pydantic_ai_repl.py
```

Type prompts like *"Add a memory that I like coding"* or *"Search for my hobbies"* to see the tools in action.

---

## 5. Mode B: Smithery (HTTP / Hosted Simulation)

Smithery allows you to run the MCP server as an HTTP endpoint, simulating a hosted deployment.

### Start the Dev Server

```bash
uv run smithery dev
```

This will output something like:
`Server running at http://127.0.0.1:8080/mcp`

### Use the Playground

Smithery provides a web interface to test tools without writing code.

```bash
uv run smithery playground
```

This opens a browser tab. You can select tools like `add_memory` from the UI, fill in the JSON arguments, and execute them against your local server.

### Troubleshooting Smithery

-   **"Server reference not found"**: Ensure `pyproject.toml` contains the `[tool.smithery]` block and that `src/mem0_mcp_server/server.py` exports a function decorated with `@smithery.server`.
-   **"Module not found"**: Ensure you installed with `pip install -e ".[smithery]"` or `uv sync`.

---

## 6. Mode C: Docker

Test the exact container image that would be deployed to production.

### Build the Image

```bash
docker build -t mem0-mcp-server .
```

### Run the Container

The Docker container **needs** the API key passed explicitly.

```bash
docker run --rm \
  -e MEM0_API_KEY="sk_mem0_..." \
  -p 8081:8081 \
  mem0-mcp-server
```

The server is now listening on port 8081.

### Testing Docker Connection

To verify the Docker container is working, point the Agent REPL to it using the provided config.

1.  **Keep the Docker container running** in one terminal.
2.  **In a new terminal**, run the agent:

```bash
export MEM0_MCP_CONFIG_PATH="$PWD/example/docker-config.json"
export MEM0_API_KEY="sk_mem0_..." # Still needed for the Agent itself

python example/pydantic_ai_repl.py
```

If the agent connects, you will see logs in the Docker terminal window.

---

## 7. Connecting Claude Desktop / Cursor

To use your **local source code** in Claude Desktop (instead of the PyPI package):

1.  Open your config file:
    *   **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
    *   **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2.  Add/Modify the `mem0` entry to point to your local path:

```json
{
  "mcpServers": {
    "mem0-local": {
      "command": "uv",
      "args": [
        "run",
        "--from",
        "/ABSOLUTE/PATH/TO/mem0-mcp-server",
        "mem0-mcp-server"
      ],
      "env": {
        "MEM0_API_KEY": "sk_mem0_..."
      }
    }
  }
}
```

3.  Restart Claude Desktop. The `mem0-local` server should now appear with a "connected" icon.

---

## 8. Config File Reference

When creating custom configurations (e.g., for specific Smithery deployments), use these templates.

**Standard Stdio Config (`config.json`)**
Used for local binaries or running via `uvx`.

```json
{
  "mcpServers": {
    "mem0": {
      "command": "uvx",
      "args": ["mem0-mcp-server"],
      "env": {
        "MEM0_API_KEY": "..."
      }
    }
  }
}
```

**HTTP Config**
Used for Smithery or Docker endpoints.

```json
{
  "mcpServers": {
    "mem0-http": {
      "type": "http",
      "url": "http://localhost:8081/mcp"
    }
  }
}
```
