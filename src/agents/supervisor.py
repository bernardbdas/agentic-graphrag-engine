"""Supervisor Agent orchestrating LangGraph multi-agent execution pipeline."""

from __future__ import annotations

import logging
import time

from ..graph.neo4j_client import Neo4jClient
from ..rag.hybrid_retriever import HybridRetriever
from ..schemas.models import (
    FinancialAnalysisRequest,
    FinancialAnalysisResponse,
    VerificationReport,
)
from .financial_analyst import FinancialAnalystAgent
from .graph_retriever import GraphRetrievalAgent
from .state import AgentGraphState
from .verifier import VerifierAgent

logger = logging.getLogger("graphrag.supervisor")


class SupervisorAgent:
    """Coordinates state transitions between graph retrieval, synthesis, and verification."""

    def __init__(self, neo4j_client: Neo4jClient, hybrid_retriever: HybridRetriever):
        self.neo4j = neo4j_client
        self.retriever = hybrid_retriever
        self.graph_agent = GraphRetrievalAgent(neo4j_client, hybrid_retriever)
        self.analyst_agent = FinancialAnalystAgent()
        self.verifier_agent = VerifierAgent()

    async def run(self, request: FinancialAnalysisRequest) -> FinancialAnalysisResponse:
        start_time = time.time()

        # Initial state setup
        state: AgentGraphState = {
            "query": request.query,
            "tickers": request.tickers,
            "iteration": 0,
            "graph_context": {},
            "retrieved_chunks": [],
            "draft_synthesis": "",
            "verification_report": VerificationReport(is_verified=False, confidence_score=0.0),
            "reasoning_trace": [],
            "final_response": "",
            "is_complete": False,
        }

        # Step 1: Retrieval
        step1_out = await self.graph_agent.execute(state)
        state.update(step1_out)  # type: ignore

        # Step 2: Synthesis
        step2_out = await self.analyst_agent.execute(state)
        state.update(step2_out)  # type: ignore

        # Step 3: Verification
        step3_out = await self.verifier_agent.execute(state)
        state.update(step3_out)  # type: ignore

        latency_ms = (time.time() - start_time) * 1000.0

        return FinancialAnalysisResponse(
            query=request.query,
            tickers=request.tickers,
            synthesis=state["final_response"],
            reasoning_trace=state["reasoning_trace"],
            retrieved_evidence=state["retrieved_chunks"],
            graph_context_subgraph=state["graph_context"],
            verification=state["verification_report"],
            latency_ms=round(latency_ms, 2),
        )
