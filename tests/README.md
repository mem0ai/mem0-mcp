# Mem0 MCP Tests

This directory contains test scripts for the Mem0 MCP (Model Control Protocol) server and its functionality. The tests are designed to verify that the memory storage, retrieval, and search functions are working correctly.

## Overview

The test suite includes:

1. **Unit Tests**: Test individual functions in isolation

   - `test_add_coding_preference.py`: Tests for adding memories with project metadata
   - `test_get_all_coding_preferences.py`: Tests for retrieving all memories by project
   - `test_search_coding_preferences.py`: Tests for semantic search functionality

2. **Integration Tests**: Test the complete workflow

   - `test_integration.py`: Tests for combined functionality across multiple operations

3. **Mock Implementation**:
   - `conftest.py`: Contains the mock implementation of the Mem0 API client

## Running the Tests

### Using the Test Runner Script (Recommended)

We provide a convenient shell script to run tests:

```bash
# Make the script executable (if needed)
chmod +x tests/run_tests.sh

# Run all tests
./tests/run_tests.sh

# View all options
./tests/run_tests.sh --help
```

### Manual Test Execution

To run all tests using uv:

```bash
uv run -m pytest tests/
```

To run specific test files:

```bash
uv run -m pytest tests/test_add_coding_preference.py
```

To run tests with increased verbosity:

```bash
uv run -m pytest tests/ -v
```

## Test Coverage

The tests cover:

- Adding code snippets with project-specific metadata
- Retrieving all snippets for a specific project
- Searching for code snippets using semantic search
- Error handling for all operations
- Project isolation (ensuring that memories are properly organized by project)
- Testing with both the default project and custom projects

## API Version

These tests support both v1 (deprecated) and v2 of the Mem0 API. The main implementation has been updated to use the v2 API format, which uses:

```python
# Get all memories
client.get_all(
    filters={"metadata": {"project": project_name}},
    version="v2"
)

# Search memories
client.search(
    query,
    filters={"metadata": {"project": project_name}},
    version="v2"
)
```

The mock client in `conftest.py` supports both API versions for backward compatibility with tests.

## Requirements

- pytest
- pytest-asyncio (for async test support)

Install with `uv` (the project's package manager):

```bash
uv pip install pytest pytest-asyncio
```

Or update the project dependencies:

```bash
uv pip sync
```
