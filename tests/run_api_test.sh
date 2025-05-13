#!/bin/bash
# Run real API tests for mem0-mcp

# Navigate to project root
cd "$(dirname "$0")/.." || exit

# Check if API key is configured
if [ -f .env ]; then
    echo "Found .env file with API configuration"
else
    echo "Warning: No .env file found. Make sure your API key is set in the environment."
    echo "You may need to create a .env file with your API key:"
    echo "API_KEY=your_api_key_here"
    # Continue anyway as the key might be set in the environment
fi

# Check for verbose flag
if [ "$1" = "-v" ] || [ "$1" = "--verbose" ]; then
    echo "Running API test with verbose output..."
    uv run -m tests.test_real_api --verbose
else
    echo "Running API test..."
    uv run -m tests.test_real_api
fi 