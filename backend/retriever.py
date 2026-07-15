"""
ACL-filtered document retrieval from vector database.
"""
from typing import List, Optional, Dict
import os
import re
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from llm_client import embed_text

# Initialize Qdrant client (configure connection in production)
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
COLLECTION_NAME = "finance_documents"

# Retrieval tuning knobs for larger corpora
HYBRID_CANDIDATE_MULTIPLIER = int(os.getenv("HYBRID_CANDIDATE_MULTIPLIER", "8"))
HYBRID_LEXICAL_POOL_LIMIT = int(os.getenv("HYBRID_LEXICAL_POOL_LIMIT", "1500"))
HYBRID_RRF_K = float(os.getenv("HYBRID_RRF_K", "60"))
RERANK_DENSE_WEIGHT = float(os.getenv("RERANK_DENSE_WEIGHT", "0.60"))
RERANK_LEXICAL_WEIGHT = float(os.getenv("RERANK_LEXICAL_WEIGHT", "0.40"))
RERANK_FUSION_WEIGHT = float(os.getenv("RERANK_FUSION_WEIGHT", "0.35"))


def _tokenize(text: str) -> List[str]:
    """Lowercase tokenization for lexical scoring."""
    return re.findall(r"[a-z0-9]+", (text or "").lower())


def _keyword_score(query: str, content: str) -> float:
    """Simple lexical relevance score for keyword retrieval."""
    query_tokens = _tokenize(query)
    content_tokens = _tokenize(content)
    if not query_tokens or not content_tokens:
        return 0.0

    content_set = set(content_tokens)
    matches = sum(1 for token in query_tokens if token in content_set)
    coverage = matches / max(len(set(query_tokens)), 1)
    density = matches / max(len(content_tokens), 1)
    return (0.85 * coverage) + (0.15 * density)


def _normalize_scores(scores: Dict[str, float]) -> Dict[str, float]:
    """Normalize scores to [0, 1] for stable fusion/rerank weighting."""
    if not scores:
        return {}
    min_score = min(scores.values())
    max_score = max(scores.values())
    if max_score == min_score:
        return {k: 1.0 for k in scores}
    return {k: (v - min_score) / (max_score - min_score) for k, v in scores.items()}


def retrieve_documents(
    query: str,
    user_id: Optional[str] = None,
    filters: Optional[Dict] = None,
    limit: int = 10
) -> List[Dict]:
    """
    Retrieve documents from vector database with ACL filtering.
    Uses hybrid retrieval (dense + lexical), then reranks and diversifies results.
    
    Args:
        query: User's search query
        user_id: User ID for ACL filtering (None = no ACL filter, for admins)
        filters: Additional metadata filters
        limit: Maximum number of documents to return
        
    Returns:
        List of relevant documents with metadata
    """
    print(f"DEBUG retriever: Searching with user_id={user_id}")
    
    # Build ACL filter only if user_id is provided
    if user_id:
        acl_filter = Filter(
            must=[
                FieldCondition(
                    key="acl",
                    match=MatchValue(value=user_id)
                )
            ]
        )
    else:
        # No ACL filter for admins
        acl_filter = None
    
    # Add additional filters if provided
    if filters:
        if not acl_filter:
            acl_filter = Filter(must=[])
        for key, value in filters.items():
            acl_filter.must.append(
                FieldCondition(key=key, match=MatchValue(value=value))
            )
    try:
        # Generate query embedding for dense retrieval
        query_vector = embed_text(query)

        candidate_limit = limit * HYBRID_CANDIDATE_MULTIPLIER

        # Dense retrieval from Qdrant vector similarity
        dense_results = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            query_filter=acl_filter,
            limit=candidate_limit
        ).points

        # Lexical retrieval over a bounded candidate pool
        lexical_pool, _ = client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=acl_filter,
            limit=max(candidate_limit * 5, HYBRID_LEXICAL_POOL_LIMIT),
            with_payload=True,
            with_vectors=False
        )

        lexical_ranked = []
        for point in lexical_pool:
            content = point.payload.get("content", "")
            score = _keyword_score(query, content)
            if score > 0:
                lexical_ranked.append((point, score))
        lexical_ranked.sort(key=lambda x: x[1], reverse=True)
        lexical_ranked = lexical_ranked[:candidate_limit]

        # Build rank/score maps for fusion and reranking
        dense_rank = {}
        dense_score = {}
        candidate_points = {}
        for idx, point in enumerate(dense_results, start=1):
            pid = str(point.id)
            dense_rank[pid] = idx
            dense_score[pid] = float(point.score)
            candidate_points[pid] = point

        lexical_rank = {}
        lexical_score = {}
        for idx, (point, score) in enumerate(lexical_ranked, start=1):
            pid = str(point.id)
            lexical_rank[pid] = idx
            lexical_score[pid] = float(score)
            # Keep dense result objects when available because they carry vector scores.
            if pid not in candidate_points:
                candidate_points[pid] = point

        normalized_dense = _normalize_scores(dense_score)
        normalized_lexical = _normalize_scores(lexical_score)

        # Hybrid fusion via Reciprocal Rank Fusion (RRF)
        rrf_k = HYBRID_RRF_K
        fused = []
        for pid, point in candidate_points.items():
            dense_rrf = 1.0 / (rrf_k + dense_rank[pid]) if pid in dense_rank else 0.0
            lexical_rrf = 1.0 / (rrf_k + lexical_rank[pid]) if pid in lexical_rank else 0.0
            fused_score = dense_rrf + lexical_rrf

            # Second-stage rerank score on fused candidates
            rerank_score = (
                (RERANK_DENSE_WEIGHT * normalized_dense.get(pid, 0.0)) +
                (RERANK_LEXICAL_WEIGHT * normalized_lexical.get(pid, 0.0)) +
                (RERANK_FUSION_WEIGHT * fused_score)
            )
            fused.append((point, rerank_score))

        fused.sort(key=lambda x: x[1], reverse=True)
        reranked_points = [point for point, _ in fused[:candidate_limit]]

        # Diversify results: prefer one chunk per unique document
        documents = []
        seen_files = set()
        remaining_results = []

        # First pass: one chunk per unique file
        for result in reranked_points:
            source_file = result.payload.get("source_file", "")
            if source_file and source_file not in seen_files:
                seen_files.add(source_file)
                documents.append({
                    "id": result.id,
                    "content": result.payload.get("content", ""),
                    "title": source_file,
                    "metadata": {
                        "page_number": result.payload.get("page_number"),
                        "source_file": source_file,
                        "chunk_index": result.payload.get("chunk_index")
                    },
                    "score": float(getattr(result, "score", 0.0))
                })
            else:
                remaining_results.append(result)
            
            if len(documents) >= limit:
                break

        # Second pass: fill remaining slots with best matches
        for result in remaining_results:
            if len(documents) >= limit:
                break
            documents.append({
                "id": result.id,
                "content": result.payload.get("content", ""),
                "title": result.payload.get("source_file", ""),
                "metadata": {
                    "page_number": result.payload.get("page_number"),
                    "source_file": result.payload.get("source_file"),
                    "chunk_index": result.payload.get("chunk_index")
                },
                "score": float(getattr(result, "score", 0.0))
            })
        
        print(
            f"DEBUG retriever: Returning {len(documents)} documents from {len(seen_files)} "
            f"unique files using hybrid retrieval + reranking"
        )
        return documents
        
    except Exception as e:
        print(f"Error retrieving documents: {e}")
        import traceback
        traceback.print_exc()
        return []
