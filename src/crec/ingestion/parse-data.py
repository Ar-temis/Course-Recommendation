from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings
from crec.config import config

embed_model = HuggingFaceEndpointEmbeddings(model=config.tei_url)

text = "What is deep learning?"

query_result = embed_model.embed_query(text)
print(query_result[:3])
