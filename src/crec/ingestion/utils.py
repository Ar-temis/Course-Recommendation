from pathlib import Path
import os


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
