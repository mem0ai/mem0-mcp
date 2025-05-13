#!/bin/bash
# Run tests for the mem0-mcp server

# Navigate to project root
cd "$(dirname "$0")/.." || exit

# Check if an argument is provided
if [ $# -eq 0 ]; then
    # Run all tests with normal verbosity
    echo "Running all tests..."
    uv run -m pytest tests/
elif [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    # Display help information
    echo "Test Runner for mem0-mcp"
    echo "Usage:"
    echo "  ./tests/run_tests.sh             Run all tests"
    echo "  ./tests/run_tests.sh -v          Run all tests with verbose output"
    echo "  ./tests/run_tests.sh -vv         Run all tests with very verbose output"
    echo "  ./tests/run_tests.sh --coverage  Run tests with coverage report"
    echo "  ./tests/run_tests.sh add         Run only add_coding_preference tests"
    echo "  ./tests/run_tests.sh get         Run only get_all_coding_preferences tests"
    echo "  ./tests/run_tests.sh search      Run only search_coding_preferences tests"
    echo "  ./tests/run_tests.sh integration Run only integration tests"
elif [ "$1" = "-v" ]; then
    # Run tests with verbose output
    echo "Running all tests with verbose output..."
    uv run -m pytest tests/ -v
elif [ "$1" = "-vv" ]; then
    # Run tests with very verbose output
    echo "Running all tests with very verbose output..."
    uv run -m pytest tests/ -vv
elif [ "$1" = "--coverage" ]; then
    # Run tests with coverage report
    echo "Running tests with coverage report..."
    uv run -m pytest tests/ --cov=. --cov-report=term-missing
elif [ "$1" = "add" ]; then
    # Run only add_coding_preference tests
    echo "Running add_coding_preference tests..."
    uv run -m pytest tests/test_add_coding_preference.py -v
elif [ "$1" = "get" ]; then
    # Run only get_all_coding_preferences tests
    echo "Running get_all_coding_preferences tests..."
    uv run -m pytest tests/test_get_all_coding_preferences.py -v
elif [ "$1" = "search" ]; then
    # Run only search_coding_preferences tests
    echo "Running search_coding_preferences tests..."
    uv run -m pytest tests/test_search_coding_preferences.py -v
elif [ "$1" = "integration" ]; then
    # Run only integration tests
    echo "Running integration tests..."
    uv run -m pytest tests/test_integration.py -v
else
    echo "Unknown option: $1"
    echo "Use --help for available options"
    exit 1
fi 