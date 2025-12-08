from pprint import pprint
from crec.config import config
import sqlite3

with sqlite3.connect(config.schedule_db) as conn:
    cursor = conn.cursor()

    results = cursor.execute(
        """
        SELECT DISTINCT(subject)
        FROM spring_schedule
    """
    ).fetchall()

    pprint(results)
# client = chromadb.PersistentClient(config.chroma_path)
#
#
# collection = client.get_or_create_collection(
#     name=config.courses_col,
#     embedding_function=OllamaEmbeddingFunction(
#         model_name=config.embedding,
#     ),
# )
#
# results = collection.query(
#     query_texts=["Environmental Science / Biogeochemistry description"],
#     n_results=5,
# )
#
# pprint(results)
