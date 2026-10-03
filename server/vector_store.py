from typing import Any, List

import chromadb
import requests

from config import Config
from documents import DocumentChunk


def get_chroma_client():
    """
    Create and return a persistent Chroma client.

    TODO:
    - Use Config.CHROMA_PATH as the local storage path.
    - Return a chromadb.PersistentClient.
    """
    return chromadb.PersistentClient(path=Config.CHROMA_PATH)


def get_or_create_collection():
    """
    Get or create the Chroma collection for the knowledge assistant.

    TODO:
    - Use get_chroma_client().
    - Use Config.COLLECTION_NAME as the collection name.
    - Return the collection.
    """
    client = get_chroma_client()
    return client.get_or_create_collection(name=Config.COLLECTION_NAME)


def get_embedding(text: str) -> list[float]:
    """
    Create an embedding for a piece of text using the local model service.

    TODO:
    - Send a POST request to the Ollama embed endpoint (https://docs.ollama.com/api/embed).
    - Use Config.OLLAMA_BASE_URL.
    - Use Config.EMBEDDING_MODEL.
    - Return the embedding list from the response.

    Endpoint:
        POST {OLLAMA_BASE_URL}/api/embed

    Example request body:
        {
            "model": Config.EMBEDDING_MODEL,
            "prompt": text
        }
    """
    response = requests.post(
        f"{Config.OLLAMA_BASE_URL.rstrip('/')}/api/embed",
        json={
            "model": Config.EMBEDDING_MODEL,
            "input": text,
        },
        timeout=120,
    )
    response.raise_for_status()

    return response.json()["embeddings"][0]


def seed_vector_store(chunks: List[DocumentChunk]) -> int:
    """
    Add document chunks to the Chroma collection.

    TODO:
    - Get or create the collection.
    - Convert each chunk into:
        - id
        - document text
        - metadata with source, title, and chunk_index
        - embedding
    - Add or update the chunks in Chroma (recommend using collection.upsert(...) to prevent duplicating existing records).
    - Return the number of chunks added.

    Keep source metadata because the frontend needs to display sources.
    """
    if not chunks:
        return 0

    collection = get_or_create_collection()

    collection.upsert(
        ids=[chunk.id for chunk in chunks],
        documents=[chunk.text for chunk in chunks],
        metadatas=[
            {
                "source": chunk.source,
                "title": chunk.title,
                "chunk_index": chunk.chunk_index,
            }
            for chunk in chunks
        ],
        embeddings=[get_embedding(chunk.text) for chunk in chunks],
    )

    return len(chunks)


def retrieve_relevant_chunks(question: str, top_k: int | None = None) -> list[dict[str, Any]]:
    """
    Retrieve relevant chunks for a user question.

    TODO:
    - Create an embedding for the question.
    - Query the Chroma collection.
    - Return a list of dictionaries with:
        - text
        - source
        - title
        - chunk_index
        - optional distance or score

    The RAG workflow expects a list shaped like this:

        [
            {
                "text": "Relevant source text...",
                "source": "product_support.txt",
                "title": "Product Support Guide",
                "chunk_index": 0
            }
        ]
    """
    collection = get_or_create_collection()
    count = collection.count()

    if count == 0:
        return []

    limit = Config.TOP_K if top_k is None else top_k

    if limit < 1:
        raise ValueError("top_k must be at least 1.")

    results = collection.query(
        query_embeddings=[get_embedding(question)],
        n_results=min(limit, count),
        include=["documents", "metadatas", "distances"],
    )

    return [
        {
            "text": text,
            "source": metadata["source"],
            "title": metadata["title"],
            "chunk_index": metadata["chunk_index"],
            "distance": distance,
        }
        for text, metadata, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ]