import dspy
from pydantic import BaseModel, ConfigDict
from typing import Optional


class ConversationMemoryEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: str
    content: str


class ConversationMemory(dspy.Module):
    def __init__(self):
        super().__init__()
        self.history: list[ConversationMemoryEntry] = []
        self.summary: str = ""

    def history_str(self, l: int = 0, r: Optional[int] = None):
        if r is None:
            r = len(self.history)

        return "\n".join(
            [
                i.model_dump_json(indent=4)
                for i in self.history[l:r]
                if not isinstance(i, dict)
            ]
        )

    def forward(self, role: str, content: str):
        new_entry = ConversationMemoryEntry(role=role, content=content)
        self.history.append(new_entry)
