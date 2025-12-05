"""MCP server that exposes Mem0 REST endpoints as MCP tools."""

from __future__ import annotations

import json
import logging
import os
from typing import Annotated, Any, Callable, Dict, Optional, TypeVar

from dotenv import load_dotenv
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from mem0 import MemoryClient
from mem0.exceptions import MemoryError
from pydantic import Field

try:  # Support both package (`python -m mem0_mcp.server`) and script (`python mem0_mcp/server.py`) runs.
    from .schemas import (
        AddMemoryArgs,
        ConfigSchema,
        DeleteAllArgs,
        DeleteEntitiesArgs,
        GetMemoriesArgs,
        SearchMemoriesArgs,
        ToolMessage,
    )
except ImportError:  # pragma: no cover - fallback for script execution
    from schemas import (
        AddMemoryArgs,
        ConfigSchema,
        DeleteAllArgs,
        DeleteEntitiesArgs,
        GetMemoriesArgs,
        SearchMemoriesArgs,
        ToolMessage,
    )

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s | %(message)s")
logger = logging.getLogger("mem0_mcp_server")




T = TypeVar("T")

try:
    from smithery.decorators import smithery
except ImportError:  # pragma: no cover - Smithery optional

    class _SmitheryFallback:
        @staticmethod
        def server(*args, **kwargs):  # type: ignore[misc]
            def decorator(func: Callable[..., T]) -> Callable[..., T]:  # type: ignore[type-var]
                return func

            return decorator

    smithery = _SmitheryFallback()  # type: ignore[assignment]


# graph remains off by default , also set the default user_id to "mem0-mcp" when nothing set
ENV_API_KEY = os.getenv("MEM0_API_KEY")
ENV_DEFAULT_USER_ID = os.getenv("MEM0_DEFAULT_USER_ID", "mem0-mcp")
ENV_ENABLE_GRAPH_DEFAULT = os.getenv("MEM0_ENABLE_GRAPH_DEFAULT", "false").lower() in {
    "1",
    "true",
    "yes",
}

_CLIENT_CACHE: Dict[str, MemoryClient] = {}


def _config_value(source: Any, field: str):
    if source is None:
        return None
    if isinstance(source, dict):
        return source.get(field)
    return getattr(source, field, None)


def _with_default_filters(
    default_user_id: str, filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Ensure filters exist and include the default user_id at the top level."""
    if not filters:
        return {"AND": [{"user_id": default_user_id}]}
    if not any(key in filters for key in ("AND", "OR", "NOT")):
        filters = {"AND": [filters]}
    has_user = json.dumps(filters, sort_keys=True).find('"user_id"') != -1
    if not has_user:
        and_list = filters.setdefault("AND", [])
        if not isinstance(and_list, list):
            raise ValueError("filters['AND'] must be a list when present.")
        and_list.insert(0, {"user_id": default_user_id})
    return filters


def _mem0_call(func, *args, **kwargs):
    try:
        result = func(*args, **kwargs)
    except MemoryError as exc:  # surface structured error back to MCP client
        logger.error("Mem0 call failed: %s", exc)
        # returns the erorr to the model
        return json.dumps(
            {
                "error": str(exc),
                "status": getattr(exc, "status", None),
                "payload": getattr(exc, "payload", None),
            },
            ensure_ascii=False,
        )
    return json.dumps(result, ensure_ascii=False)


def _resolve_settings(ctx: Context | None) -> tuple[str, str, bool]:
    session_config = getattr(ctx, "session_config", None)
    api_key = _config_value(session_config, "mem0_api_key") or ENV_API_KEY
    if not api_key:
        raise RuntimeError(
            "MEM0_API_KEY is required (via Smithery config, session config, or environment) to run the Mem0 MCP server."
        )

    default_user = _config_value(session_config, "default_user_id") or ENV_DEFAULT_USER_ID
    enable_graph_default = _config_value(session_config, "enable_graph_default")
    if enable_graph_default is None:
        enable_graph_default = ENV_ENABLE_GRAPH_DEFAULT

    return api_key, default_user, enable_graph_default


# init the client
def _mem0_client(api_key: str) -> MemoryClient:
    client = _CLIENT_CACHE.get(api_key)
    if client is None:
        client = MemoryClient(api_key=api_key)
        _CLIENT_CACHE[api_key] = client
    return client


def _default_enable_graph(enable_graph: Optional[bool], default: bool) -> bool:
    if enable_graph is None:
        return default
    return enable_graph


@smithery.server(config_schema=ConfigSchema)
def create_server() -> FastMCP:
    """Create a FastMCP server usable via stdio, Docker, or Smithery."""

    # When running inside Smithery, the platform probes the server without user-provided
    # session config, so we defer the hard requirement for MEM0_API_KEY until a tool call.
    if not ENV_API_KEY:
        logger.warning(
            "MEM0_API_KEY is not set; Smithery health checks will pass, but every tool "
            "invocation will fail until a key is supplied via session config or env vars."
        )

    server = FastMCP(
        "mem0",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8081")),
        transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
    )

    # graph is disabled by default to make queries simpler and fast
    # Mention " Enable/Use graph while calling memory " in your system prompt to run it in each instance

    @server.tool(description="Store a new preference, fact, or conversation snippet. Requires at least one: user_id, agent_id, or run_id.")
    def add_memory(
        text: Annotated[
            str,
            Field(
                description="Plain sentence summarizing what to store. Required even if `messages` is provided."
            ),
        ],
        messages: Annotated[
            Optional[list[Dict[str, str]]],
            Field(
                default=None,
                description="Structured conversation history with `role`/`content`. "
                "Use when you have multiple turns.",
            ),
        ] = None,
        user_id: Annotated[
            Optional[str],
            Field(default=None, description="Override the default user scope for this write."),
        ] = None,
        agent_id: Annotated[
            Optional[str], Field(default=None, description="Optional agent identifier.")
        ] = None,
        app_id: Annotated[
            Optional[str], Field(default=None, description="Optional app identifier.")
        ] = None,
        run_id: Annotated[
            Optional[str], Field(default=None, description="Optional run identifier.")
        ] = None,
        metadata: Annotated[
            Optional[Dict[str, Any]],
            Field(default=None, description="Attach arbitrary metadata JSON to the memory."),
        ] = None,
        enable_graph: Annotated[
            Optional[bool],
            Field(
                default=None,
                description="Set true only if the caller explicitly wants Mem0 graph memory.",
            ),
        ] = None,
        ctx: Context | None = None,
    ) -> str:
        """Write durable information to Mem0."""

        api_key, default_user, graph_default = _resolve_settings(ctx)
        args = AddMemoryArgs(
            text=text,
            messages=[ToolMessage(**msg) for msg in messages] if messages else None,
            user_id=user_id if user_id else (default_user if not (agent_id or run_id) else None),
            agent_id=agent_id,
            app_id=app_id,
            run_id=run_id,
            metadata=metadata,
            enable_graph=_default_enable_graph(enable_graph, graph_default),
        )
        payload = args.model_dump(exclude_none=True)
        payload.setdefault("enable_graph", graph_default)
        conversation = payload.pop("messages", None)
        if not conversation:
            derived_text = payload.pop("text", None)
            if derived_text:
                conversation = [{"role": "user", "content": derived_text}]
            else:
                return json.dumps(
                    {
                        "error": "messages_missing",
                        "detail": "Provide either `text` or `messages` so Mem0 knows what to store.",
                    },
                    ensure_ascii=False,
                )
        else:
            payload.pop("text", None)

        client = _mem0_client(api_key)
        return _mem0_call(client.add, conversation, **payload)

    @server.tool(
        description="""Run a semantic search over existing memories.

        Use filters to narrow results. Common filter patterns:
        - Single user: {"AND": [{"user_id": "john"}]}
        - Agent memories: {"AND": [{"agent_id": "agent_name"}]}
        - Recent memories: {"AND": [{"user_id": "john"}, {"created_at": {"gte": "2024-01-01"}}]}
        - Multiple users: {"AND": [{"user_id": {"in": ["john", "jane"]}}]}
        - Cross-entity: {"OR": [{"user_id": "john"}, {"agent_id": "agent_name"}]}

        user_id is automatically added to filters if not provided.
        """
    )
    def search_memories(
        query: Annotated[str, Field(description="Natural language description of what to find.")],
        filters: Annotated[
            Optional[Dict[str, Any]],
            Field(default=None, description="Additional filter clauses (user_id injected automatically)."),
        ] = None,
        limit: Annotated[
            Optional[int], Field(default=None, description="Maximum number of results to return.")
        ] = None,
        enable_graph: Annotated[
            Optional[bool],
            Field(
                default=None,
                description="Set true only when the user explicitly wants graph-derived memories.",
            ),
        ] = None,
        ctx: Context | None = None,
    ) -> str:
        """Semantic search against existing memories."""

        api_key, default_user, graph_default = _resolve_settings(ctx)
        args = SearchMemoriesArgs(
            query=query,
            filters=filters,
            limit=limit,
            enable_graph=_default_enable_graph(enable_graph, graph_default),
        )
        payload = args.model_dump(exclude_none=True)
        payload["filters"] = _with_default_filters(default_user, payload.get("filters"))
        payload.setdefault("enable_graph", graph_default)
        client = _mem0_client(api_key)
        return _mem0_call(client.search, **payload)

    @server.tool(
        description="""Page through memories using filters instead of search.

        Use filters to list specific memories. Common filter patterns:
        - Single user: {"AND": [{"user_id": "john"}]}
        - Agent memories: {"AND": [{"agent_id": "agent_name"}]}
        - Recent memories: {"AND": [{"user_id": "john"}, {"created_at": {"gte": "2024-01-01"}}]}
        - Multiple users: {"AND": [{"user_id": {"in": ["john", "jane"]}}]}

        Pagination: Use page (1-indexed) and page_size for browsing results.
        user_id is automatically added to filters if not provided.
        """
    )
    def get_memories(
        filters: Annotated[
            Optional[Dict[str, Any]],
            Field(default=None, description="Structured filters; user_id injected automatically."),
        ] = None,
        page: Annotated[
            Optional[int], Field(default=None, description="1-indexed page number when paginating.")
        ] = None,
        page_size: Annotated[
            Optional[int], Field(default=None, description="Number of memories per page (default 10).")
        ] = None,
        enable_graph: Annotated[
            Optional[bool],
            Field(
                default=None,
                description="Set true only if the caller explicitly wants graph-derived memories.",
            ),
        ] = None,
        ctx: Context | None = None,
    ) -> str:
        """List memories via structured filters or pagination."""

        api_key, default_user, graph_default = _resolve_settings(ctx)
        args = GetMemoriesArgs(
            filters=filters,
            page=page,
            page_size=page_size,
            enable_graph=_default_enable_graph(enable_graph, graph_default),
        )
        payload = args.model_dump(exclude_none=True)
        payload["filters"] = _with_default_filters(default_user, payload.get("filters"))
        payload.setdefault("enable_graph", graph_default)
        client = _mem0_client(api_key)
        return _mem0_call(client.get_all, **payload)

    @server.tool(
        description="Delete every memory in the given user/agent/app/run but keep the entity."
    )
    def delete_all_memories(
        user_id: Annotated[
            Optional[str], Field(default=None, description="User scope to delete; defaults to server user.")
        ] = None,
        agent_id: Annotated[
            Optional[str], Field(default=None, description="Optional agent scope to delete.")
        ] = None,
        app_id: Annotated[
            Optional[str], Field(default=None, description="Optional app scope to delete.")
        ] = None,
        run_id: Annotated[
            Optional[str], Field(default=None, description="Optional run scope to delete.")
        ] = None,
        ctx: Context | None = None,
    ) -> str:
        """Bulk-delete every memory in the confirmed scope."""

        api_key, default_user, _ = _resolve_settings(ctx)
        args = DeleteAllArgs(
            user_id=user_id or default_user,
            agent_id=agent_id,
            app_id=app_id,
            run_id=run_id,
        )
        payload = args.model_dump(exclude_none=True)
        client = _mem0_client(api_key)
        return _mem0_call(client.delete_all, **payload)

    @server.tool(description="List which users/agents/apps/runs currently hold memories.")
    def list_entities(ctx: Context | None = None) -> str:
        """List users/agents/apps/runs with stored memories."""

        api_key, _, _ = _resolve_settings(ctx)
        client = _mem0_client(api_key)
        return _mem0_call(client.users)

    @server.tool(description="Fetch a single memory once you know its memory_id.")
    def get_memory(
        memory_id: Annotated[str, Field(description="Exact memory_id to fetch.")],
        ctx: Context | None = None,
    ) -> str:
        """Retrieve a single memory once the user has picked an exact ID."""

        api_key, _, _ = _resolve_settings(ctx)
        client = _mem0_client(api_key)
        return _mem0_call(client.get, memory_id)

    @server.tool(description="Overwrite an existing memory’s text.")
    def update_memory(
        memory_id: Annotated[str, Field(description="Exact memory_id to overwrite.")],
        text: Annotated[str, Field(description="Replacement text for the memory.")],
        ctx: Context | None = None,
    ) -> str:
        """Overwrite an existing memory’s text after the user confirms the exact memory_id."""

        api_key, _, _ = _resolve_settings(ctx)
        client = _mem0_client(api_key)
        return _mem0_call(client.update, memory_id=memory_id, text=text)

    @server.tool(description="Delete one memory after the user confirms its memory_id.")
    def delete_memory(
        memory_id: Annotated[str, Field(description="Exact memory_id to delete.")],
        ctx: Context | None = None,
    ) -> str:
        """Delete a memory once the user explicitly confirms the memory_id to remove."""

        api_key, _, _ = _resolve_settings(ctx)
        client = _mem0_client(api_key)
        return _mem0_call(client.delete, memory_id)

    @server.tool(
        description="Remove a user/agent/app/run record entirely (and cascade-delete its memories)."
    )
    def delete_entities(
        user_id: Annotated[
            Optional[str], Field(default=None, description="Delete this user and its memories.")
        ] = None,
        agent_id: Annotated[
            Optional[str], Field(default=None, description="Delete this agent and its memories.")
        ] = None,
        app_id: Annotated[
            Optional[str], Field(default=None, description="Delete this app and its memories.")
        ] = None,
        run_id: Annotated[
            Optional[str], Field(default=None, description="Delete this run and its memories.")
        ] = None,
        ctx: Context | None = None,
    ) -> str:
        """Delete a user/agent/app/run (and its memories) once the user confirms the scope."""

        api_key, _, _ = _resolve_settings(ctx)
        args = DeleteEntitiesArgs(
            user_id=user_id,
            agent_id=agent_id,
            app_id=app_id,
            run_id=run_id,
        )
        if not any([args.user_id, args.agent_id, args.app_id, args.run_id]):
            return json.dumps(
                {
                    "error": "scope_missing",
                    "detail": "Provide user_id, agent_id, app_id, or run_id before calling delete_entities.",
                },
                ensure_ascii=False,
            )
        payload = args.model_dump(exclude_none=True)
        client = _mem0_client(api_key)
        return _mem0_call(client.delete_users, **payload)

    # Add a simple prompt for server capabilities
    @server.prompt()
    def memory_assistant() -> str:
        """Get help with memory operations and best practices."""
        return """You are using the Mem0 MCP server for long-term memory management.

Quick Start:
1. Store memories: Use add_memory to save facts, preferences, or conversations
2. Search memories: Use search_memories for semantic queries
3. List memories: Use get_memories for filtered browsing
4. Update/Delete: Use update_memory and delete_memory for modifications

Filter Examples:
- User memories: {"AND": [{"user_id": "john"}]}
- Agent memories: {"AND": [{"agent_id": "agent_name"}]}
- Recent only: {"AND": [{"user_id": "john"}, {"created_at": {"gte": "2024-01-01"}}]}

Tips:
- user_id is automatically added to filters
- Use "*" as wildcard for any non-null value
- Combine filters with AND/OR/NOT for complex queries"""

    return server


def main() -> None:
    """Run the MCP server over stdio."""

    server = create_server()
    logger.info("Starting Mem0 MCP server (default user=%s)", ENV_DEFAULT_USER_ID)
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
