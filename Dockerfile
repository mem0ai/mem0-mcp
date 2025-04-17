# Use the official Python image with version 3.12
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy only necessary files to the container
COPY . .

# Install uv and project dependencies
RUN pip install uv && uv pip install --system .

# Expose the correct port
EXPOSE 17171

# Command to run the MCP server
CMD ["uv", "run", "main.py", "--port", "17171"]