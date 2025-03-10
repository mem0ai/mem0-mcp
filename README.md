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

Or if you're using the metadata tagging version:

```bash
uv run main_metadata_tagging.py
```

2. In Cursor, connect to the SSE endpoint, follow this [doc](https://docs.cursor.com/context/model-context-protocol) for reference:

```text
http://0.0.0.0:8080/sse
```

3. Open the Composer in Cursor and switch to `Agent` mode.

## Prompt Examples

Here are examples of how to effectively use each of the tools provided by this MCP server:

### Adding Coding Preferences

When you want to store a code snippet, implementation pattern, or programming knowledge, use prompts like these:

```text
Please save this React custom hook for fetching data with caching:

import { useState, useEffect } from 'react';

export const useFetchWithCache = (url, options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check cache first
    const cachedData = sessionStorage.getItem(`cache_${url}`);

    if (cachedData) {
      setData(JSON.parse(cachedData));
      setLoading(false);
      return;
    }

    const fetchData = async () => {
      try {
        const response = await fetch(url, options);
        if (!response.ok) throw new Error(`HTTP error ${response.status}`);

        const result = await response.json();

        // Cache the result
        sessionStorage.setItem(`cache_${url}`, JSON.stringify(result));

        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [url, JSON.stringify(options)]);

  return { data, loading, error };
};

This is a React hook (React 18) that fetches data from an API and implements caching using sessionStorage to improve performance. It handles loading states and error conditions gracefully.

```

For project-specific storage (with metadata tagging):

```text
Please save this PostgreSQL query pattern for efficient pagination in the "database-patterns" project:

SELECT *
FROM table_name
WHERE id > (SELECT id FROM table_name ORDER BY id LIMIT 1 OFFSET $offset)
ORDER BY id
LIMIT $limit;

This pattern uses keyset pagination which is more efficient than OFFSET/LIMIT for large datasets as it avoids scanning through offset rows each time. It works best with indexed columns like id.
```

### Retrieving All Coding Preferences

When you want to review all stored coding patterns:

```text

Please show me all the coding patterns we've stored so far.

```

For project-specific retrieval:

```text

Can you retrieve all the coding preferences we've saved for the "database-patterns" project?

```

### Searching Coding Preferences

When you need to find specific coding patterns or solutions:

```text

Find me any React hooks we've saved for handling API requests.

```

```text

Search for efficient pagination patterns in SQL databases.

```

```text

Do we have any examples of implementing authentication in Express.js?

```

For project-specific searches:

```text

Within the "frontend-components" project, search for any modal implementation patterns.

```

## Effective Workflow

For the most effective use of this system:

1. **Consistently Store Valuable Code**: Whenever you encounter or create a useful code pattern, implementation, or solution, store it with thorough documentation.

2. **Always Search First**: Before implementing a solution, search the stored preferences to see if you already have a pattern for it.

3. **Use Project Tags**: Organize related code patterns using project tags to keep your knowledge base well-structured.

4. **Include Context**: When storing code, always include:
   - The programming language/framework and version
   - Any dependencies or prerequisites
   - Example usage
   - Edge cases or limitations
   - Performance considerations

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

```bash

uv run main.py --host <your host> --port <your port>

```

The server exposes an SSE endpoint at `/sse` that MCP clients can connect to for accessing the coding preferences management tools.
