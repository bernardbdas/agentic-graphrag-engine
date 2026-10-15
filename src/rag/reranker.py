"""Late-interaction cross-encoder reranker leveraging ColBERTv2 semantics."""

from __future__ import annotations

import logging

from ..schemas.models import RetrievedChunk

logger = logging.getLogger("graphrag.reranker")


class ColBERTReranker:
    """Reranker implementing token-level late interaction scoring."""

    def __init__(self, model_name: str = "colbert-ir/colbertv2.0"):
        self.model_name = model_name
        self._model = None
        self._init_model()

    def _init_model(self) -> None:
        try:
            from ragatouille import RAGPretrainedModel

            self._model = RAGPretrainedModel.from_pretrained(self.model_name)
            logger.info("Loaded RAGatouille ColBERTv2 model: %s", self.model_name)
        except Exception as e:
            logger.warning(
                "RAGatouille / ColBERTv2 not available locally (%s). Using BM25+Exact Match hybrid ranker.",
                e,
            )
            self._model = None

    def rerank(
        self, query: str, candidates: list[RetrievedChunk], top_k: int = 5
    ) -> list[RetrievedChunk]:
        """Rerank candidate passages against the query."""
        if not candidates:
            return []

        if self._model:
            try:
                passages = [c.text for c in candidates]
                results = self._model.rerank(query=query, documents=passages, k=top_k)
                # Map scores back to chunks
                reranked_chunks: list[RetrievedChunk] = []
                for res in results:
                    orig_idx = res["result_index"]
                    chunk = candidates[orig_idx]
                    chunk.rerank_score = float(res["score"])
                    reranked_chunks.append(chunk)
                return reranked_chunks
            except Exception as e:
                logger.error("ColBERT reranking failed: %s. Falling back to heuristic reranker.", e)

        # Fallback scoring: Lexical overlap + density score + base vector score
        query_terms = set(query.lower().split())
        for chunk in candidates:
            chunk_words = chunk.text.lower().split()
            overlap_count = sum(1 for w in chunk_words if w in query_terms)
            overlap_ratio = overlap_count / max(len(query_terms), 1)
            # Combine vector cosine score (0.0 to 1.0) with exact keyword density
            combined_score = (chunk.vector_score * 0.6) + (overlap_ratio * 0.4)
            chunk.rerank_score = round(combined_score, 4)

        # Sort descending by rerank_score
        sorted_chunks = sorted(candidates, key=lambda c: c.rerank_score or 0.0, reverse=True)
        return sorted_chunks[:top_k]
