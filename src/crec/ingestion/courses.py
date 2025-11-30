import re
import hashlib
from pathlib import Path
from pypdf import PdfReader

from crec.config import config
import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)
from utils import sanitize_directory


def parse_course_descriptions(pdf_path):
    """Extract and parse course information from PDF."""

    # Extract text from PDF
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

    # Regex pattern to match course entries
    pattern = (
        r"([A-Z]+\s+\d{3})\s+([^\(]+)\((\d+)\s+credits?\)(.*?)(?=\n[A-Z]+\s+\d{3}\s+|$)"
    )

    courses = []
    matches = re.finditer(pattern, text, re.DOTALL)

    for match in matches:
        course_code = match.group(1).strip()
        course_name = match.group(2).strip()
        credits = match.group(3).strip()
        full_text = match.group(4).strip()

        # Extract prerequisites
        prereq_pattern = (
            r"((?:Prerequisite\(s\)|Pre/Co-requisite\(s\)):\s*.+?)(?=\n\n|\Z)"
        )
        prereq_match = re.search(prereq_pattern, full_text, re.DOTALL)
        prerequisites = prereq_match.group(1).strip() if prereq_match else None

        # Extract description (everything before prerequisites)
        if prerequisites:
            # Split on either format
            desc_split = re.split(
                r"(?:Prerequisite\(s\)|Pre/Co-requisite\(s\)):", full_text
            )
            description = desc_split[0].strip()
        else:
            description = full_text.strip()

        courses.append(
            {
                "course_code": course_code,
                "course_name": course_name,
                "credits": credits,
                "description": description,
                "prerequisites": prerequisites,
            }
        )

    return courses


def pipeline(folder: Path | str):

    paths = sanitize_directory(folder)
    client = chromadb.PersistentClient(path=config.chroma_path)

    try:
        client.delete_collection("courses")
    except ValueError as e:
        print("Warning:", e)

    collection = client.get_or_create_collection(
        name="courses",
        embedding_function=OllamaEmbeddingFunction(model_name=config.embedding),
    )
    for file_path in paths:
        file_name = Path(file_path).name

        if not file_name.startswith("ug_bulletin"):
            continue

        print(f"Reading file: {file_name}")

        courses = parse_course_descriptions(file_path)
        for course in courses:
            print(f"Adding course: {course.get('course_code')}")
            text = str(course)
            id = hashlib.md5(text.encode()).hexdigest()
            collection.add(
                ids=[id],
                documents=[text],
                metadatas=[
                    {
                        "file_name": file_name,
                        "course_code": course.get("course_code"),
                        "course_name": course.get("course_name"),
                    }
                ],
            )


pipeline("/home/artemis/Developer/Course-Recommendation/data/")
