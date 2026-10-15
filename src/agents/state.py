"""LangGraph state representation for Multi-Agent Financial Synthesis."""

from __future__ import annotations

from typing import Any, TypedDict

from ..schemas.models import AgentThoughtStep, RetrievedChunk, VerificationReport


class AgentGraphState(TypedDict):
    """Shared immutable state passed across the LangGraph multi-agent DAG."""

    query: str
    tickers: list[str]
    iteration: int
    graph_context: dict[str, Any]
    retrieved_chunks: list[RetrievedChunk]
    draft_synthesis: str
    verification_report: VerificationReport
    reasoning_trace: list[AgentThoughtStep]
    final_response: str
    is_complete: bool
