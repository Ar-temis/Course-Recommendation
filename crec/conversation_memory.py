from mem0 import Memory
from pydantic import BaseModel, ConfigDict
from typing import Optional
import datetime


class MemoryTools:
    """Tools for interacting with the Mem0 memory system."""

    def __init__(self, memory_config: dict):
        self.memory = Memory.from_config(memory_config)

    def store_memory(
        self,
        content: list[dict[str, str]],
        user_id: str = "default_user",
    ) -> str:
        """Store information in memory."""
        try:
            self.memory.add(content, user_id=user_id)
            return f"Stored memory: {content}"
        except Exception as e:
            return f"Error storing memory: {str(e)}"

    def search_memories(
        self,
        query: str,
        # user_id: str = "default_user",
        limit: int = 5,
    ) -> str:
        """Search for long-term memories

        This tool can also retrieve informations you have saved
        in your previous conversations with the user.
        """
        try:
            results = self.memory.search(query, user_id="default_user", limit=limit)
            if not results:
                return "No relevant memories found."

            memory_text = "Relevant memories found:\n"
            for i, result in enumerate(results["results"]):
                memory_text += f"{i}. {result['memory']}\n"
            return memory_text
        except Exception as e:
            return f"Error searching memories: {str(e)}"

    def get_all_memories(
        self,
        # user_id: str = "default_user",
    ) -> str:
        """Get all memories for a user."""
        try:
            results = self.memory.get_all(user_id="default_user")
            if not results:
                return "No memories found for this user."

            memory_text = "All memories for user:\n"
            for i, result in enumerate(results["results"]):
                memory_text += f"{i}. {result['memory']}\n"
            return memory_text
        except Exception as e:
            return f"Error retrieving memories: {str(e)}"

    def update_memory(self, memory_id: str, new_content: str) -> str:
        """Update an existing memory."""
        try:
            self.memory.update(memory_id, new_content)
            return f"Updated memory with new content: {new_content}"
        except Exception as e:
            return f"Error updating memory: {str(e)}"

    def delete_memory(self, memory_id: str) -> str:
        """Delete a specific memory."""
        try:
            self.memory.delete(memory_id)
            return "Memory deleted successfully."
        except Exception as e:
            return f"Error deleting memory: {str(e)}"


def get_current_time() -> str:
    """Get the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class ConversationMemoryEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: str
    content: str


class ConversationMemory:
    def __init__(self):
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

    def save(self, role: str, content: str):
        new_entry = ConversationMemoryEntry(role=role, content=content)
        self.history.append(new_entry)
