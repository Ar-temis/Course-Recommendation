from langchain_ollama import OllamaEmbeddings
import chromadb

from crec.config import config


def setup() -> (chromadb.PersistentClient, OllamaEmbeddings):
    client = chromadb.PersistentClient(path=config.chroma_path)
    embed_model = OllamaEmbeddings(model=config.embedding)
    return client, embed_model


client, model = setup()

embed = model.embed_query("hello word")
print(embed)
