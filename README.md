[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/mem0ai-mem0-mcp-badge.png)](https://mseep.ai/app/mem0ai-mem0-mcp)

# MCP Server with Mem0 for Managing Coding Preferences

This demonstrates a structured approach for using an [MCP](https://modelcontextprotocol.io/introduction) server with [mem0](https://mem0.ai) to manage coding preferences efficiently. The server can be used with Cursor and provides essential tools for storing, retrieving, and searching coding preferences.

## Installation

1. Clone this repository
2. Initialize the `uv` environment:

```bash
uv venv
```

3. Activate the virtual environment:

```bash
source .venv/bin/activate
```

4. Install the dependencies using `uv`:

```bash
# Install in editable mode from pyproject.toml
uv pip install -e .
```

5. Update `.env` file in the root directory with your mem0 API key:

```bash
MEM0_API_KEY=your_api_key_here
```

## Usage

1. Start the MCP server:

```bash
uv run main.py
```

2. In Cursor, connect to the SSE endpoint, follow this [doc](https://docs.cursor.com/context/model-context-protocol) for reference:

```
http://0.0.0.0:8080/sse
```

3. Open the Composer in Cursor and switch to `Agent` mode.

## Demo with Cursor

https://github.com/user-attachments/assets/56670550-fb11-4850-9905-692d3496231c

## Features

The server provides three main tools for managing code preferences:

1. `add_coding_preference`: Store code snippets, implementation details, and coding patterns with comprehensive context including:
   - Complete code with dependencies
   - Language/framework versions
   - Setup instructions
   - Documentation and comments
   - Example usage
   - Best practices

2. `get_all_coding_preferences`: Retrieve all stored coding preferences to analyze patterns, review implementations, and ensure no relevant information is missed.

3. `search_coding_preferences`: Semantically search through stored coding preferences to find relevant:
   - Code implementations
   - Programming solutions
   - Best practices
   - Setup guides
   - Technical documentation

## Why?

This implementation allows for a persistent coding preferences system that can be accessed via MCP. The SSE-based server can run as a process that agents connect to, use, and disconnect from whenever needed. This pattern fits well with "cloud-native" use cases where the server and clients can be decoupled processes on different nodes.

### Server

By default, the server runs on 0.0.0.0:8080 but is configurable with command line arguments like:

```
uv run main.py --host <your host> --port <your port>
```

The server exposes an SSE endpoint at `/sse` that MCP clients can connect to for accessing the coding preferences management tools.

