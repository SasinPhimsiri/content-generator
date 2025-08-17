"""RAG system for style prompting and few-shot learning."""

from .simple_vector_store import simple_rag_system, SimpleVectorStore

__all__ = [
    "simple_rag_system",
    "SimpleVectorStore"
]
