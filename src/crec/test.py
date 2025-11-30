from pprint import pprint
from crec.ingestion.setup import setup

client, model = setup()

collection = client.get_or_create_collection("courses")

query = model.embed_query("Compsci 203")

results = collection.query(
    query_embeddings=query, where={"course_code": "COMPSCI 203"}, n_results=5
)

pprint(results)
