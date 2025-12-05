"""Shared Pydantic models for the Mem0 MCP server."""

from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


# classic structure across all payloads , does not change
class ToolMessage(BaseModel):
    role: str = Field(..., description="Role of the speaker, e.g., user or assistant.")
    content: str = Field(..., description="Full text of the utterance to store.")


class ConfigSchema(BaseModel):
    """Session-level overrides used when hosting via Smithery or HTTP."""

    mem0_api_key: str = Field(..., description="Mem0 API key (required)")
    default_user_id: Optional[str] = Field(
        None, description="Default user_id injected into filters when unspecified."
    )
    enable_graph_default: Optional[bool] = Field(
        None, description="Default enable_graph toggle when clients omit the flag."
    )


class AddMemoryArgs(BaseModel):
    text: Optional[str] = Field(
        None, description="Simple sentence to remember; converted into a user message when set."
    )
    messages: Optional[list[ToolMessage]] = Field(
        None,
        description=(
            "Explicit role/content history for durable storage. Provide this OR `text`; defaults "
            "to the server user_id."
        ),
    )
    user_id: Optional[str] = Field(None, description="Override for the Mem0 user ID.")
    agent_id: Optional[str] = Field(None, description="Optional agent identifier.")
    app_id: Optional[str] = Field(None, description="Optional app identifier.")
    run_id: Optional[str] = Field(None, description="Optional run identifier.")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Opaque metadata to persist.")
    enable_graph: Optional[bool] = Field(
        None, description="Only set True if the user explicitly opts into graph storage."
    )


# this is where we start with filters
class SearchMemoriesArgs(BaseModel):
    query: str = Field(..., description="Describe what you want to find.")
    filters: Optional[Dict[str, Any]] = Field(
        None, description="Additional filter clauses; user_id is injected automatically."
    )
    limit: Optional[int] = Field(None, description="Optional maximum number of matches.")
    enable_graph: Optional[bool] = Field(
        None, description="Set True only when the user asks for graph knowledge."
    )


class GetMemoriesArgs(BaseModel):
    filters: Optional[Dict[str, Any]] = Field(
        None, description="Structured filters; user_id injected automatically."
    )
    page: Optional[int] = Field(None, description="1-indexed page number.")
    page_size: Optional[int] = Field(None, description="Number of memories per page.")
    enable_graph: Optional[bool] = Field(
        None, description="Set True only when the user wants graph knowledge."
    )


class DeleteAllArgs(BaseModel):
    user_id: Optional[str] = Field(
        None, description="User scope to delete; defaults to server user."
    )
    agent_id: Optional[str] = Field(None, description="Optional agent scope filter.")
    app_id: Optional[str] = Field(None, description="Optional app scope filter.")
    run_id: Optional[str] = Field(None, description="Optional run scope filter.")


class DeleteEntitiesArgs(BaseModel):
    user_id: Optional[str] = Field(None, description="Delete this user and all related memories.")
    agent_id: Optional[str] = Field(None, description="Delete this agent and its memories.")
    app_id: Optional[str] = Field(None, description="Delete this app and its memories.")
    run_id: Optional[str] = Field(None, description="Delete this run and its memories.")
