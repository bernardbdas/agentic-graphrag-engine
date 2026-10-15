"""FastAPI Application entrypoint for Agentic GraphRAG Engine."""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .agents.supervisor import SupervisorAgent
from .graph.neo4j_client import Neo4jClient
from .rag.hybrid_retriever import HybridRetriever
from .schemas.models import (
    FinancialAnalysisRequest,
    FinancialAnalysisResponse,
    GraphQueryRequest,
    HybridSearchQuery,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("graphrag.api")

neo4j_client = Neo4jClient()
retriever = HybridRetriever()
supervisor = SupervisorAgent(neo4j_client, retriever)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Agentic GraphRAG Engine...")
    await neo4j_client.connect()
    yield
    logger.info("Shutting down Agentic GraphRAG Engine...")
    await neo4j_client.close()


app = FastAPI(
    title="Agentic GraphRAG Engine",
    description="Multi-Agent Knowledge Graph & Hybrid Vector Financial Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, Any]:
    return {
        "status": "healthy",
        "service": "agentic-graphrag-engine",
        "neo4j_connected": neo4j_client._is_connected,
    }


@app.post("/api/v1/analyze", response_model=FinancialAnalysisResponse)
async def analyze_financial_query(request: FinancialAnalysisRequest) -> FinancialAnalysisResponse:
    """Execute multi-agent GraphRAG reasoning pipeline."""
    try:
        response = await supervisor.run(request)
        return response
    except Exception as e:
        logger.exception("Error executing financial query: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/graph/subgraph")
async def get_multihop_subgraph(request: GraphQueryRequest) -> dict[str, Any]:
    """Retrieve multi-hop subgraphs for visual exploration."""
    return await neo4j_client.query_multihop_subgraph(
        ticker=request.ticker,
        depth=request.depth,
        relationship_types=request.relationship_filters,
    )


@app.post("/api/v1/search/hybrid")
async def hybrid_search(query: HybridSearchQuery) -> dict[str, Any]:
    """Execute vector + keyword search with ColBERT reranking."""
    results = await retriever.retrieve(
        query=query.query_text,
        tickers=[query.ticker] if query.ticker else None,
        top_k_vector=query.top_k_vector,
        top_k_rerank=query.top_k_rerank,
    )
    return {"query": query.query_text, "results": results, "count": len(results)}


frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8001, reload=True)
