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

## Setup

Before proceeding, ensure you have created a `.env` file in the root directory with the following content:

```
MEM0_API_KEY=<your-api-key>
HOST=<your-host> # Optional, defaults to 0.0.0.0
PORT=<your-port> # Optional, defaults to 8080
```

Replace `<your-api-key>`, `<your-host>`, and `<your-port>` with your actual values. These variables are required for the application to function correctly, except `HOST` and `PORT`, which have default values.

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

## Using Docker

To run the MCP server with Docker, follow these steps:

1. Build and start the Docker container using `docker-compose`:

```bash
docker-compose up --build -d
```

This command will build the Docker image and start the container in detached mode.

2. Verify that the container is running:

```bash
docker ps
```

You should see the `mem0-server` container listed.

3. Access the MCP server at the configured endpoint:

```
http://<your-host>:<your-port>/sse
```

Replace `<your-host>` and `<your-port>` with the values you set in the `.env` file.

4. To stop the container, use:

```bash
docker-compose down
```

This will stop and remove the container.

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

