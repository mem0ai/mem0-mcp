# Pydantic AI Demo

This directory contains a Pydantic AI agent to interactively test the Mem0 MCP server.

## Quick Start

```bash
# Install the package
pip install mem0-mcp-server
# Or with uv
uv pip install mem0-mcp-server

# Set your API keys
export MEM0_API_KEY="m0-..."
export OPENAI_API_KEY="sk-openai_..."

# Run the REPL
python example/pydantic_ai_repl.py
```

## Using Different Server Configurations

### Local Server (default)
```bash
python example/pydantic_ai_repl.py
```

### Docker Container
```bash
# Start Docker container
docker run --rm -d \
  --name mem0-mcp \
  -e MEM0_API_KEY="m0-..." \
  -p 8080:8081 \
  mem0-mcp-server

# Run agent pointing to Docker
export MEM0_MCP_CONFIG_PATH=example/docker-config.json
export MEM0_MCP_CONFIG_SERVER=mem0-docker
python example/pydantic_ai_repl.py
```

### Smithery Remote Server
```bash
export MEM0_MCP_CONFIG_PATH=example/config-smithery.json
export MEM0_MCP_CONFIG_SERVER=mem0-memory-mcp
python example/pydantic_ai_repl.py
```

## What Happens

1. The script loads the configuration from `example/config.json` by default
2. Starts or connects to the Mem0 MCP server
3. A Pydantic AI agent (Mem0Guide) connects to the server
4. You get an interactive REPL to test memory operations

## Example Prompts

- "Remember that I love tiramisu"
- "Search for my food preferences"
- "Update my project: the mobile app is now 80% complete"
- "Show me all memories about project Phoenix"
- "Delete memories from 2023"

## Config Files

- `config.json` - Local server (default)
- `docker-config.json` - Connect to Docker container on port 8080
- `config-smithery.json` - Connect to Smithery remote server

You can create custom configs by copying and modifying these files.