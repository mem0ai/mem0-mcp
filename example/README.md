# Pydantic AI Demo

This directory lets you run the Mem0 MCP server end-to-end with the bundled
Pydantic AI agent without touching `uvx` or Smithery.

## Requirements

```bash
pip install -e ".[smithery]"   # or uv pip install -e ".[smithery]"
export MEM0_API_KEY="sk_mem0_..."
export OPENAI_API_KEY="sk-openai_..."
```

## Run the REPL

```bash
python example/pydantic_ai_repl.py
```

What happens:

1. The script loads `example/config.json`, which points to your local
   `mem0_mcp_server.server` module (`python -m mem0_mcp_server.server`).
2. The Mem0 MCP server starts over stdio with whatever env vars you exported.
3. A Pydantic AI agent (Mem0Guide) connects to that server and drops you into a
   REPL. Type prompts like “remember that I love tiramisu” or “search memories
   for tiramisu” to exercise the tools.

### Custom configs

- Set `MEM0_MCP_CONFIG_PATH=/path/to/another/config.json` to point the agent to
  a different MCP endpoint (e.g., your Smithery deployment or Docker container).
- Use `MEM0_MCP_CONFIG_SERVER` if the config file defines multiple servers.

This flow mirrors the original bundled script but lives entirely in this
`example/` directory with ready-to-use config so the REPL “just works” for local
testing.

## Configuring Other Transports

The two config files in this folder cover the most common setups:

- `config.json` – launches your local checkout via stdio (`python -m mem0_mcp_server.server`).
- `docker-config.json` – points at an HTTP server on `http://localhost:8081/mcp` (e.g., the Docker container).

You can copy either file and tweak the `command`/`args` or `type`/`url` fields
to match other environments—or reuse them directly in other MCP clients (Claude,
Cursor, custom apps). The Pydantic REPL is just a convenient example of how any
client would connect once it has the right config.

- **Local stdio (default)** – runs `python -m mem0_mcp_server.server`. No edits
  needed; the REPL launches the server from your working tree.
- **uvx / published package** – change `command` to `"uvx"` and `args` to
  `["mem0-mcp-server"]` if you want to test the installed CLI instead of your
  repo checkout.
- **Docker / hosted HTTP** – expose the container on `http://localhost:8081/mcp`
  (or your host URL) and create a config that uses Pydantic’s HTTP transport,
  e.g. `example/docker-config.json`. Set `MEM0_MCP_CONFIG_PATH` to that file
  before running the REPL.
- **Smithery-hosted HTTP** – once deployed, copy the Smithery URL
  (`https://server.smithery.ai/.../mcp`) into the same HTTP config shape above
  so the REPL talks to the hosted server instead of starting a local process.

In all cases you can select the desired server definition with
`MEM0_MCP_CONFIG_SERVER` if your config file contains multiple entries.
