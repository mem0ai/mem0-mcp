# Use the official Python image with version 3.12
FROM python:3.12-slim
# Set the working directory
WORKDIR /app

# Copy only necessary files to the container
COPY . .

# Install uv and project dependencies
RUN pip install uv && uv pip install --system .

# Set environment variable for the port
ENV PORT=8080

# Expose the correct port
EXPOSE ${PORT}

# Command to run the MCP server
CMD ["uv", "run", "main.py"]