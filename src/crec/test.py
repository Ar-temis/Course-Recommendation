from pprint import pprint
from crec.config import config
import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)

client = chromadb.PersistentClient(config.chroma_path)


collection = client.get_or_create_collection(
    name=config.courses_col,
    embedding_function=OllamaEmbeddingFunction(
        model_name=config.embedding,
    ),
)

results = collection.query(
    query_texts=["Environmental Science / Biogeochemistry description"],
    n_results=5,
)

pprint(results)
