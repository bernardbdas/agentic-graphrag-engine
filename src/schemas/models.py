from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class EntityNode(BaseModel):
    """Knowledge graph node representing financial entities."""

    id: str = Field(..., description="Unique entity identifier (e.g., CIK or Ticker)")
    name: str = Field(..., description="Entity legal name")
    type: str = Field(
        ..., description="Entity category: Corporation, Executive, Subsidiary, Metric, Risk"
    )
    properties: dict[str, Any] = Field(default_factory=dict, description="Metadata key-value pairs")


class RelationshipEdge(BaseModel):
    """Knowledge graph edge representing financial dependencies and ownership."""

    source_id: str
    target_id: str
    relation_type: str = Field(..., description="E.g., OWNS, SUPPLIES, COMPETES_WITH, AUDITS")
    weight: float = Field(default=1.0, ge=0.0, le=1.0)
    properties: dict[str, Any] = Field(default_factory=dict)


class GraphQueryRequest(BaseModel):
    """Request payload for multi-hop graph retrieval."""

    ticker: str = Field(
        ..., min_length=1, max_length=10, description="Target company ticker symbol"
    )
    depth: int = Field(default=2, ge=1, le=5, description="Max traversal depth in graph")
    relationship_filters: list[str] | None = Field(
        default=None,
        description="Optional filter on edge types (e.g. ['SUPPLIES', 'SUBSIDIARY_OF'])",
    )


class HybridSearchQuery(BaseModel):
    """Query payload combining dense vector retrieval and structured Cypher filters."""

    query_text: str = Field(..., min_length=3, description="Financial research query")
    ticker: str | None = None
    fiscal_year: int | None = None
    top_k_vector: int = Field(default=20, ge=1, le=100)
    top_k_rerank: int = Field(default=5, ge=1, le=20)


class RetrievedChunk(BaseModel):
    """Document passage retrieved from multi-stage search."""

    chunk_id: str
    doc_id: str
    ticker: str
    text: str
    source_filing: str = Field(..., description="E.g. '10-K FY2023', '10-Q Q3 2024'")
    vector_score: float
    rerank_score: float | None = None
    entities_detected: list[str] = Field(default_factory=list)


class AgentThoughtStep(BaseModel):
    """Traceable reasoning step executed by an agent."""

    step_number: int
    agent_name: str
    action: str
    input_payload: dict[str, Any]
    output_summary: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class VerificationReport(BaseModel):
    """Cross-verification check on factual consistency and numerical integrity."""

    is_verified: bool
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    hallucination_detected: bool = False
    discrepancies: list[str] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)


class FinancialAnalysisRequest(BaseModel):
    """Primary user query input for financial reasoning."""

    query: str = Field(..., min_length=5, description="Financial synthesis or supply-chain query")
    tickers: list[str] = Field(..., min_items=1, description="Target company tickers")
    require_verification: bool = Field(default=True)


class FinancialAnalysisResponse(BaseModel):
    """Final synthesized response containing multi-agent reasoning, citations, and metrics."""

    query: str
    tickers: list[str]
    synthesis: str = Field(..., description="Comprehensive multi-perspective financial synthesis")
    reasoning_trace: list[AgentThoughtStep] = Field(default_factory=list)
    retrieved_evidence: list[RetrievedChunk] = Field(default_factory=list)
    graph_context_subgraph: dict[str, Any] = Field(default_factory=dict)
    verification: VerificationReport
    latency_ms: float
