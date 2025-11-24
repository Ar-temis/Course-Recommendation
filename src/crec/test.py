from pprint import pprint
from crec.ingestion.setup import setup
from crec.config import config

client, model = setup()

collection = client.get_or_create_collection(config.major_req_col)

query = model.embed_query("Environmental Science / Biogeochemistry")

results = collection.query(query_embeddings=[query], n_results=5)

pprint(results)
