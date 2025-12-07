# used to create vector db out of documents
import hashlib
import logging
from queue import Queue
from threading import Thread
from pathlib import Path

import chromadb
from langchain_ollama import OllamaEmbeddings
from crec.config import config
from langchain_text_splitters import HTMLSemanticPreservingSplitter

from utils import sanitize_directory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

log = logging.getLogger(__file__)
log.setLevel(logging.INFO)


# Reader worker: Parses HTMLs
# TODO: Should make this function take in more datatypes
def reader_worker(html_paths: str, buffer: Queue):
    HEADERS = [
        ("h1", "Header 1"),
        ("h2", "Header 2"),
        ("h4", "Header 4"),
    ]

    splitter = HTMLSemanticPreservingSplitter(
        headers_to_split_on=HEADERS,
        separators=["\n\n", "\n", ". ", "! ", "? "],
        max_chunk_size=1024,
        chunk_overlap=32,
        elements_to_preserve=["table", "ul", "ol"],
        denylist_tags=["script", "style", "head"],
    )
    for path in html_paths:
        log.info(f"Reading {path}")

        with open(path, "r", encoding="utf-8") as f:
            splits = splitter.split_text(f)
            transformed_splits = [
                {
                    "page_content": " ".join(
                        [
                            split_doc.metadata.get("Header 4", ""),
                            split_doc.page_content,
                        ]
                    ),
                    "metadata": {
                        "file_name": Path(path).name,
                        **split_doc.metadata,
                    },
                }
                for split_doc in splits
            ]
            buffer.put((path, transformed_splits))
    buffer.put(None)
    log.info("Done!")


# Embedding worker: Embeds split HTMLs
def embed_worker(buffer: Queue):
    client = chromadb.PersistentClient(path=config.chroma_path)
    embed_model = OllamaEmbeddings(model=config.embedding)

    try:
        client.delete_collection(config.major_req_col)
    except ValueError as e:
        print("Warning:", e)

    collection = client.get_or_create_collection(
        config.major_req_col,
    )

    while True:
        item = buffer.get()

        if item is None:
            log.info("Buffer Empty. Exiting.")
            break

        path, splits = item
        log.info(f"Generating embeddings for {path}")

        for split in splits:
            text = split.get("page_content")
            embedding = embed_model.embed_query(text)
            id = hashlib.md5(text.encode()).hexdigest()
            collection.add(
                ids=[id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[split.get("metadata")],
            )
        log.info(f"Finished embedding: {path}")


# Main function
def pipeline(folder: str) -> None:
    """Reader, writer pipeline using threading"""

    paths = sanitize_directory(folder)

    html_paths = [p for p in paths if p.endswith(".html")]

    buffer = Queue(maxsize=5)

    reader_thread = Thread(target=reader_worker, args=(html_paths, buffer))
    embed_thread = Thread(target=embed_worker, args=(buffer,))

    reader_thread.start()
    embed_thread.start()

    reader_thread.join()
    embed_thread.join()

    log.info("Done!")


pipeline("/home/artemis/Developer/Course-Recommendation/data/")
# if __name__ == "__main__":
#     if len(sys.argv) > 1:
#         pipeline(sys.argv[1])
#     else:
#         print("Error: Target folder not set. Append it after when calling this script.")
