"""Neo4j Client with resilient connection pooling and multi-hop Cypher traversal."""

from __future__ import annotations

import logging
from typing import Any

from neo4j import AsyncDriver, AsyncGraphDatabase

from .schema import GRAPH_CONSTRAINTS, SAMPLE_FINANCIAL_TRIPLES

logger = logging.getLogger("graphrag.neo4j")


class Neo4jClient:
    """Async Neo4j driver wrapper with multi-hop Cypher traversals and in-memory mock fallback."""

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "password123",
        database: str = "neo4j",
    ):
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database
        self._driver: AsyncDriver | None = None
        self._is_connected = False
        # In-memory mock store for offline testing and graceful degradation
        self._mock_triples = list(SAMPLE_FINANCIAL_TRIPLES)

    async def connect(self) -> bool:
        """Attempt connection to real Neo4j; fall back to in-memory graph if unavailable."""
        try:
            self._driver = AsyncGraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password),
                max_connection_lifetime=3600,
            )
            # Verify connectivity
            async with self._driver.session(database=self.database) as session:
                await session.run("RETURN 1 AS ping")
            self._is_connected = True
            logger.info("Connected successfully to Neo4j instance at %s", self.uri)
            await self._initialize_schema()
            return True
        except Exception as e:
            logger.warning(
                "Neo4j live connection failed: %s. Switching to in-memory mock graph engine.", e
            )
            self._is_connected = False
            return False

    async def _initialize_schema(self) -> None:
        """Execute constraints and index setup."""
        if not self._is_connected or not self._driver:
            return
        async with self._driver.session(database=self.database) as session:
            for constraint in GRAPH_CONSTRAINTS:
                try:
                    await session.run(constraint)
                except Exception as e:
                    logger.debug("Constraint init log: %s", e)

    async def close(self) -> None:
        if self._driver:
            await self._driver.close()
            self._is_connected = False

    async def query_multihop_subgraph(
        self,
        ticker: str,
        depth: int = 2,
        relationship_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """Traverse k-hops from a company node, returning ego-network subgraph."""
        ticker = ticker.upper()
        if self._is_connected and self._driver:
            rel_filter = ""
            if relationship_types:
                rel_filter = ":" + "|".join(relationship_types)

            cypher = f"""
            MATCH path = (c:Company {{ticker: $ticker}})-[r{rel_filter}*1..{depth}]-(target)
            RETURN path
            LIMIT 50
            """
            async with self._driver.session(database=self.database) as session:
                result = await session.run(cypher, ticker=ticker)
                records = await result.data()
                return self._format_neo4j_subgraph(records, ticker)
        else:
            # High-fidelity mock traversal
            return self._mock_multihop_traversal(ticker, depth)

    def _mock_multihop_traversal(self, ticker: str, depth: int) -> dict[str, Any]:
        """Perform deterministic BFS on in-memory triples."""
        visited_nodes = {ticker}
        current_level = {ticker}
        subgraph_nodes = [{"id": ticker, "name": ticker, "type": "Company"}]
        subgraph_edges = []

        for _ in range(depth):
            next_level = set()
            for edge in self._mock_triples:
                h, t = edge["head"], edge["tail"]
                if h in current_level or t in current_level:
                    subgraph_edges.append(
                        {
                            "source": h,
                            "target": t,
                            "relation": edge["rel"],
                            "weight": edge["weight"],
                        }
                    )
                    other = t if h in current_level else h
                    if other not in visited_nodes:
                        visited_nodes.add(other)
                        next_level.add(other)
                        label = edge.get(
                            "tail_label" if h in current_level else "head_label", "Entity"
                        )
                        name = edge.get("tail_name" if h in current_level else "head_name", other)
                        subgraph_nodes.append({"id": other, "name": name, "type": label})
            current_level = next_level
            if not current_level:
                break

        return {
            "root": ticker,
            "depth": depth,
            "nodes": subgraph_nodes,
            "edges": subgraph_edges,
            "node_count": len(subgraph_nodes),
            "edge_count": len(subgraph_edges),
        }

    def _format_neo4j_subgraph(
        self, records: list[dict[str, Any]], root_ticker: str
    ) -> dict[str, Any]:
        nodes_dict = {}
        edges_list = []
        for record in records:
            path = record.get("path")
            if not path:
                continue
            for node in path.nodes:
                nodes_dict[node.element_id] = {
                    "id": node.get("ticker", node.get("id", node.element_id)),
                    "name": node.get("name", "Unknown"),
                    "type": list(node.labels)[0] if node.labels else "Unknown",
                }
            for rel in path.relationships:
                edges_list.append(
                    {
                        "source": rel.start_node.get("ticker", rel.start_node.element_id),
                        "target": rel.end_node.get("ticker", rel.end_node.element_id),
                        "relation": rel.type,
                        "weight": rel.get("weight", 1.0),
                    }
                )

        return {
            "root": root_ticker,
            "nodes": list(nodes_dict.values()),
            "edges": edges_list,
            "node_count": len(nodes_dict),
            "edge_count": len(edges_list),
        }
