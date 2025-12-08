import os
import dotenv
from typing import Any, Mapping, Optional
from pathlib import Path

dotenv.load_dotenv()


def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(name, default)


class _WriteProtectedDict(dict):
    """
    A dict that raises on item assignment to discourage bypassing the Config API.
    Use Config.set / Config.update / attribute assignment instead.
    """

    def __setitem__(self, key, value):
        raise TypeError(
            "Direct mutation is disabled. Use Config.set(...) or attribute assignment."
        )  # noqa

    def update(self, *args, **kwargs):
        raise TypeError("Direct mutation is disabled. Use Config.update(...).")  # noqa


class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            inst = super().__new__(cls)
            # initialize once
            object.__setattr__(inst, "_store", {})  # raw mutable store, private
            object.__setattr__(
                inst, "_frozen_view", _WriteProtectedDict()
            )  # read-only view
            inst._initialize_defaults()
            cls._instance = inst
        return cls._instance

    # Internal: initialize defaults once
    def _initialize_defaults(self):
        db_dir = Path(__file__).parent.parent.joinpath("dbs/")
        data_dir = Path(__file__).parent.parent.joinpath("data/")
        self._store.update(
            {
                # Core
                "llm": "qwen3:8b",
                "llm_url": "http://localhost:11434",
                "llm_api_key": "",
                "llm_temperature": 0.9,
                "embedding": "embeddinggemma",
                "tei_url": "http://localhost:46515",
                "context_window": 8000,
                # Documents
                "data_dir": "/datapool/course-rec",
                "nodes_path": "/datapool/course-rec/nodes.json",
                "pipeline_cache": "./pipeline_cache",
                "majors_doc": str(data_dir.joinpath("majors.json")),
                # Chroma
                "chroma_path": str(db_dir.joinpath("chroma_data/")),
                "major_req_col": "major_req_col",
                "courses_col": "courses",
                # SQLite
                "schedule_db": str(db_dir.joinpath("schedule.db")),
                # Mem0 config
                "mem_chroma": str(db_dir.joinpath("chroma_memory")),
                "mem_col": "test",
            }
        )
        # refresh read-only view
        self._refresh_view()

    def _refresh_view(self):
        # Rebuild the read-only mapping so callers can inspect without mutating.
        object.__setattr__(
            self, "_frozen_view", _WriteProtectedDict(self._store.copy())
        )

    # Attribute access

    def __getattr__(self, key: str) -> Any:
        # Called when normal attribute lookup fails
        if key in self._store:
            return self._store[key]
        raise AttributeError(f"{type(self).__name__} has no attribute '{key}'")

    def __setattr__(self, key: str, value: Any) -> None:
        # Allow internal attributes to be set normally
        if key in {"_store", "_frozen_view"}:
            return object.__setattr__(self, key, value)
        # Route public assignments into the store
        self._store[key] = value
        self._refresh_view()

    def __delattr__(self, key: str) -> None:
        if key in {"_store", "_frozen_view"}:
            return object.__delattr__(self, key)
        if key in self._store:
            del self._store[key]
            self._refresh_view()
        else:
            raise AttributeError(f"{type(self).__name__} has no attribute '{key}'")

    # Dict-like API (preferred for bulk ops)

    def get(self, key: str, default: Any = None) -> Any:
        return self._store.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value
        self._refresh_view()

    def update(self, mapping: Mapping[str, Any] = None, **kwargs) -> None:
        if mapping:
            self._store.update(dict(mapping))
        if kwargs:
            self._store.update(kwargs)
        self._refresh_view()

    def as_dict(self) -> dict:
        # Return a shallow copy to prevent external mutation
        return dict(self._store)

    def view(self) -> Mapping[str, Any]:
        # Read-only mapping to inspect at runtime
        return self._frozen_view


# Singleton instance
config = Config()

# EXAMPLES:
# config.llm_temperature = 0.3
# config.update({"backup_llm_url": "http://localhost:18083/v1"}, response_type="Concise")
# reading safely:
# temp = config.llm_temperature
# all_values = config.as_dict()
# read-only view (raises on mutation): ro = config.view()
