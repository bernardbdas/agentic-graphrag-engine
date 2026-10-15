"""Graph & Hybrid Retrieval Agent."""

from __future__ import annotations

import logging
from typing import Any

from ..graph.neo4j_client import Neo4jClient
from ..rag.hybrid_retriever import HybridRetriever
from ..schemas.models import AgentThoughtStep
from .state import AgentGraphState

logger = logging.getLogger("graphrag.agent.retriever")


class GraphRetrievalAgent:
    """Extracts structural subgraphs and reranked SEC filing chunks."""

    def __init__(self, neo4j_client: Neo4jClient, hybrid_retriever: HybridRetriever):
        self.neo4j = neo4j_client
        self.retriever = hybrid_retriever

    async def execute(self, state: AgentGraphState) -> dict[str, Any]:
        logger.info("Executing GraphRetrievalAgent for tickers: %s", state["tickers"])

        # 1. Multi-hop Graph Traversal
        subgraph_nodes = []
        subgraph_edges = []
        for ticker in state["tickers"]:
            sg = await self.neo4j.query_multihop_subgraph(ticker=ticker, depth=2)
            subgraph_nodes.extend(sg.get("nodes", []))
            subgraph_edges.extend(sg.get("edges", []))

        merged_subgraph = {
            "nodes": {n["id"]: n for n in subgraph_nodes},
            "edges": subgraph_edges,
        }

        # 2. Hybrid Document Retrieval + ColBERT Reranking
        chunks = await self.retriever.retrieve(
            query=state["query"], tickers=state["tickers"], top_k_rerank=4
        )

        step = AgentThoughtStep(
            step_number=state["iteration"] + 1,
            agent_name="GraphRetrievalAgent",
            action="multihop_graph_and_vector_retrieval",
            input_payload={"tickers": state["tickers"], "query": state["query"]},
            output_summary=f"Extracted {len(merged_subgraph['nodes'])} graph entities and {len(chunks)} high-relevance filing chunks.",
        )

        trace = list(state.get("reasoning_trace", []))
        trace.append(step)

        return {
            "graph_context": merged_subgraph,
            "retrieved_chunks": chunks,
            "reasoning_trace": trace,
            "iteration": state["iteration"] + 1,
        }
