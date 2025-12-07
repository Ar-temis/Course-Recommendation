import re
from crec.config import config
import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)


def chroma_result_to_nodes(result: dict) -> list[dict]:
    ids = result["ids"][0]
    texts = result["documents"][0]
    metadatas = result["metadatas"][0]
    scores = result["distances"][0]

    return [
        {
            "node": {
                "node_id": ids[i],
                "text": texts[i],
                "metadata": metadatas[i],
            },
            "score": float(scores[i]),
        }
        for i in range(len(ids))
    ]


def course_retriever(course_queries: list[str]) -> list[dict]:
    """
    Retrieve courses from ChromaDB using semantic search or metadata filtering.

    Automatically detects course code patterns (e.g., "COMPSCI 101", "BIO 111")
    and applies metadata filtering for exact matches. Text-based queries use
    semantic search via embeddings.

    Args:
        course_queries (list[str]): List of search queries. Can be course codes
            in format "DEPT NNN" (e.g. "BEHAVSCI 102", "COMPSCI 101") or natural language
            queries (e.g., "introduction to programming").

    Returns:
        list[dict]: Query results from ChromaDB collection. Each result contains
            matched documents with their metadata, embeddings, and distances.
            Results are combined from both metadata-filtered and semantic searches.

    Examples:
        >>> course_retriever(["COMPSCI 101"])
        # Uses metadata filtering for exact course code match

        >>> course_retriever(["machine learning courses"])
        # Uses semantic search across course descriptions

        >>> course_retriever(["BIO 111", "introduction to chemistry"])
        # Combines metadata filtering for BIO 111 with semantic search
    """
    client = chromadb.PersistentClient(path=config.chroma_path)
    collection = client.get_or_create_collection(
        name=config.courses_col,
        embedding_function=OllamaEmbeddingFunction(
            model_name=config.embedding,
        ),
    )

    # Pattern to match course codes like "COMPSCI 101" or "BIO 111"
    course_code_pattern = re.compile(r"^[A-Z]+\s+\d+$", re.IGNORECASE)

    # Separate queries into course codes and text queries
    course_codes = []
    text_queries = []

    for query in course_queries:
        if course_code_pattern.match(query.strip()):
            course_codes.append(query.strip())
        else:
            text_queries.append(query)
    print("course_codes", course_codes)
    print("text", text_queries)

    result = []
    # If all queries are course codes, use metadata filtering
    if course_codes:
        if len(course_codes) == 1:
            where_filter = {"course_code": course_codes[0]}
        else:
            where_filter = {"$or": [{"course_code": code} for code in course_codes]}

        chroma_result = collection.query(
            query_texts=course_codes,
            n_results=1,
            where=where_filter,
        )

        result.extend(chroma_result_to_nodes(chroma_result))

    if text_queries:
        chroma_result = collection.query(
            query_texts=text_queries,
            n_results=3,
        )
        result.extend(chroma_result_to_nodes(chroma_result))
    return result


__import__("pprint").pprint(course_retriever(["available courses"]))
