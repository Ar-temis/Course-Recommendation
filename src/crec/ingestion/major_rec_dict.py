# Used to create a dictionary out of known major names
import os
import logging
import json
from queue import Queue
from threading import Thread
from pathlib import Path

from langchain_text_splitters import HTMLSemanticPreservingSplitter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

log = logging.getLogger(__file__)
log.setLevel(logging.INFO)

# Set of Header 4 values to filter for
HEADER_4_FILTER = [
    "Applied Mathematics and Computational Sciences/Computer Science",
    "Applied Mathematics and Computational Sciences/Mathematics",
    "Arts and Media/Arts",
    "Arts and Media/Media",
    "Behavioral Science / Economics",
    "Behavioral Science / Psychology",
    "Behavioral Science / Neuroscience",
    "Computation and Design / Computer Science",
    "Computation and Design / Digital Media",
    "Computation and Design / Social Policy",
    "Cultures and Societies / Cultural Anthropology",
    "Cultures and Societies / Sociology",
    "Data Science",
    "Environmental Science / Biogeochemistry",
    "Environmental Science / Biology",
    "Environmental Science / Chemistry",
    "Environmental Science / Public Policy",
    "Global China Studies",
    "Global Health / Biology",
    "Global Health / Public Policy",
    "Humanities / Creative Writing and Translation",
    "Humanities / Literature",
    "Humanities /Philosophy and Religion",
    "Humanities /World History",
    "Materials Science / Chemistry",
    "Materials Science / Physics",
    "Molecular Bioscience / Biogeochemistry",
    "Molecular Bioscience / Biophysics",
    "Molecular Bioscience / Cell and Molecular Biology",
    "Molecular Bioscience / Genetics and Genomics",
    "Molecular Bioscience / Neuroscience",
    "Philosophy, Politics, and Economics / Economic History",
    "Philosophy, Politics, and Economics / Philosophy",
    "Philosophy, Politics, and Economics / Political Science",
    "Philosophy, Politics, and Economics / Public Policy",
    "Quantitative Political Economy / Economics",
    "Quantitative Political Economy /Political Science",
    "Quantitative Political Economy /Public Policy",
]


# Helper functions
def sanitize(filename: str) -> str:
    """Return lower cased whitespace replaced with (-) str.

    Parameters
        filename (str): Filename you want to sanitize

    Returns
        str: sanitized filename
    """

    temp = filename.lower().strip()
    temp = temp.replace(" ", "_")
    return temp


def sanitize_directory(folder: str) -> list[str]:
    folder_path = Path(folder)
    sanitized_paths = []

    for file_path in folder_path.iterdir():
        if file_path.is_file():
            new_name = sanitize(file_path.name)

            # Only rename if necessary
            if new_name != file_path.name:
                new_path = file_path.with_name(new_name)
                file_path.rename(new_path)
                sanitized_paths.append(os.path.join(folder, new_name))
            else:
                sanitized_paths.append(os.path.join(folder, new_name))

    return sanitized_paths


# Reader worker: Parses HTMLs
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
            transformed_splits = []

            for split_doc in splits:
                header_4 = split_doc.metadata.get("Header 4", "")

                # Only include splits where Header 4 is in the filter set
                if header_4 in HEADER_4_FILTER:
                    transformed_splits.append(
                        {
                            "page_content": split_doc.page_content,
                            "metadata": {
                                "file_name": Path(path).name,
                                **split_doc.metadata,
                            },
                        }
                    )

            # Only put in buffer if there are filtered splits
            if transformed_splits:
                buffer.put((path, transformed_splits))

    buffer.put(None)
    log.info("Done!")


# Embedding worker: Embeds split HTMLs and writes to JSON
def embed_worker(buffer: Queue, output_json_path: str = "output.json"):
    # Load existing JSON if it exists
    if os.path.exists(output_json_path):
        with open(output_json_path, "r", encoding="utf-8") as f:
            try:
                json_data = json.load(f)
            except json.JSONDecodeError:
                json_data = {}
    else:
        json_data = {}

    while True:
        item = buffer.get()

        if item is None:
            log.info("Buffer Empty. Exiting.")
            break

        path, splits = item
        log.info(f"Generating embeddings for {path}")

        for split in splits:
            text = split.get("page_content")
            header_4 = split.get("metadata", {}).get("Header 4", "")

            # Add to JSON with Header 4 as the key
            if header_4 not in json_data:
                json_data[header_4] = []

            json_data[header_4].append(
                {
                    "text": text,
                    "metadata": split.get("metadata"),
                }
            )

        log.info(f"Finished embedding: {path}")

    # Write the final JSON to file
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    log.info(f"JSON data written to {output_json_path}")


# Main function
def pipeline(folder: str, output_json: str = "output.json") -> None:
    """Reader, writer pipeline using threading"""

    paths = sanitize_directory(folder)

    html_paths = [p for p in paths if p.endswith(".html")]

    buffer = Queue(maxsize=5)

    output_json = Path(folder).joinpath(output_json)

    reader_thread = Thread(target=reader_worker, args=(html_paths, buffer))
    embed_thread = Thread(target=embed_worker, args=(buffer, output_json))

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
