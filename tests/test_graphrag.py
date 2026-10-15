import pytest
from fastapi.testclient import TestClient

from src.agents.supervisor import SupervisorAgent
from src.graph.neo4j_client import Neo4jClient
from src.main import app
from src.rag.hybrid_retriever import HybridRetriever
from src.rag.reranker import ColBERTReranker
from src.schemas.models import (
    EntityNode,
    FinancialAnalysisRequest,
    RetrievedChunk,
)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def neo4j_mock():
    return Neo4jClient()


@pytest.fixture
def retriever():
    return HybridRetriever()


def test_schema_entity_node():
    node = EntityNode(
        id="AAPL",
        name="Apple Inc.",
        type="Corporation",
        properties={"sector": "Consumer Electronics"},
    )
    assert node.id == "AAPL"
    assert node.properties["sector"] == "Consumer Electronics"


@pytest.mark.asyncio
async def test_neo4j_mock_multihop_traversal(neo4j_mock):
    subgraph = await neo4j_mock.query_multihop_subgraph("AAPL", depth=2)
    assert subgraph["root"] == "AAPL"
    assert len(subgraph["nodes"]) >= 2
    assert any(n["id"] == "TSM" for n in subgraph["nodes"])


def test_colbert_reranker_fallback():
    reranker = ColBERTReranker()
    candidates = [
        RetrievedChunk(
            chunk_id="c1",
            doc_id="d1",
            ticker="AAPL",
            source_filing="10-K",
            text="TSMC supplies advanced 3nm chips to Apple.",
            vector_score=0.8,
        ),
        RetrievedChunk(
            chunk_id="c2",
            doc_id="d2",
            ticker="AAPL",
            source_filing="10-K",
            text="General corporate governance and board policies.",
            vector_score=0.7,
        ),
    ]
    reranked = reranker.rerank(
        query="Who supplies 3nm chips to Apple?", candidates=candidates, top_k=2
    )
    assert len(reranked) == 2
    # The first one should have high lexical and semantic match for 3nm chips
    assert reranked[0].chunk_id == "c1"


@pytest.mark.asyncio
async def test_hybrid_retriever(retriever):
    chunks = await retriever.retrieve(
        query="TSMC chip fabrication constraints", tickers=["NVDA", "AAPL"]
    )
    assert len(chunks) > 0
    assert any(c.ticker in ["NVDA", "AAPL"] for c in chunks)


@pytest.mark.asyncio
async def test_supervisor_end_to_end(neo4j_mock, retriever):
    supervisor = SupervisorAgent(neo4j_mock, retriever)
    req = FinancialAnalysisRequest(
        query="Assess single-point supply chain vulnerabilities across leading semiconductor clients.",
        tickers=["AAPL", "NVDA"],
        require_verification=True,
    )
    res = await supervisor.run(req)
    assert res.synthesis != ""
    assert len(res.reasoning_trace) == 3
    assert res.verification.is_verified is True
    assert res.latency_ms > 0


def test_api_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


def test_api_analyze(client):
    payload = {
        "query": "What are the primary geopolitical risks affecting advanced chip supply?",
        "tickers": ["AAPL", "NVDA"],
        "require_verification": True,
    }
    res = client.post("/api/v1/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "TSMC" in data["synthesis"] or "Taiwan" in data["synthesis"]
    assert len(data["reasoning_trace"]) > 0
