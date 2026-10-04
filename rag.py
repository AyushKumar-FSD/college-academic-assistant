from functools import lru_cache

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

MAX_DIST = 0.65  # ponytail: cosine-distance cutoff for "not in knowledge base"; tune on your own questions


@lru_cache
def collection():
    return chromadb.PersistentClient("vectorstore").get_or_create_collection(
        "docs", metadata={"hnsw:space": "cosine"},
        embedding_function=SentenceTransformerEmbeddingFunction("all-MiniLM-L6-v2"))


def retrieve(q, k=5):
    r = collection().query(query_texts=[q], n_results=k)
    return [{"text": d, **m} for d, m, dist in
            zip(r["documents"][0], r["metadatas"][0], r["distances"][0]) if dist <= MAX_DIST]
