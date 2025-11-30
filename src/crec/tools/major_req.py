import json
from pathlib import Path
from thefuzz import fuzz, process
from crec.config import config


def major_retriever(
    major_query: str,
) -> dict[str, list]:
    """Retrieve top matching major requirements based on fuzzy string matching.

    Searches through a JSON document containing major program information and
    returns the top 3 matches using token-based fuzzy matching.

    Args:
        major_query (str): The search query string representing a major or
            academic program name (e.g., "Computer Science", "Biogeochemistry").

    Returns:
        list: A list of dictionaries. Each dictionary includes:
            - 'text': Matched major requirements, and credit information
            - 'metadata': Dict with 'Header 4' (major name) and 'file_name' keys

    Raises:
        LookupError: If the majors document file does not exist at the
            configured path.
        json.JSONDecodeError: If the majors document contains invalid JSON.
    """

    if not Path(config.majors_doc).exists():
        msg = f"Majors document does not exist at {config.majors_doc}"
        raise LookupError(msg)

    with open(config.majors_doc, "r", encoding="utf-8") as f:
        try:
            majors = json.load(f)
        except json.JSONDecodeError:
            raise json.JSONDecodeError

    matches = process.extract(
        major_query,
        majors.keys(),
        scorer=fuzz.token_set_ratio,
        limit=3,
    )

    result = []

    for match in matches:
        result.append(majors.get(match[0]))

    return result
