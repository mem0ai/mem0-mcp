FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml README.md ./
COPY src ./src

RUN uv pip install --system .

ENV PORT=8081

CMD ["python", "-m", "mem0_mcp_server.http_entry"]
