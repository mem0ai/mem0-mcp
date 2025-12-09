# Tests

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-mock

# Run all tests
pytest

# Run specific test file
pytest tests/test_server.py

# Run with coverage
pytest --cov=src/mem0_mcp_server
```

## Test Coverage

- **test_server.py** - Core functionality (validation, filters, cache)
- **test_retry.py** - Retry logic with exponential backoff
- **test_cli.py** - CLI argument parsing

## Test Structure

```
tests/
├── __init__.py
├── test_server.py    # Core server tests
├── test_retry.py     # Retry logic tests
└── test_cli.py       # CLI argument tests
```
