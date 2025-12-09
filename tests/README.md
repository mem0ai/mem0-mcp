# Tests

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_basic.py::TestAPIKeyValidation
```

## Test Coverage

**test_basic.py** - Core logic validation (13 tests)
- API key format validation
- Default filter injection logic
- Enable graph default behavior
- CLI argument parsing format
- Retry logic calculations
- Error code detection (4xx vs 5xx)

## Test Results

```
13 passed in 0.43s
```

All tests validate the core business logic without requiring external dependencies.

