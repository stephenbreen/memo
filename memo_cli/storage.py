import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from tinydb import TinyDB, Query

# Path to the database file
DB_PATH = Path.home() / ".memo_cli" / "db.json"

class Command(BaseModel):
    id: Optional[int] = None
    text: str
    description: str
    tally: int = 0
    last_used: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)

class Database:
    def __init__(self, db_path: Path = DB_PATH):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = TinyDB(db_path)
        self.table = self.db.table("commands")

    def add_command(self, text: str, description: str, tags: List[str] = None) -> int:
        command = Command(text=text, description=description, tags=tags or [])
        doc_id = self.table.insert(command.dict(exclude={"id"}))
        return doc_id

    def list_commands(self) -> List[Command]:
        docs = self.table.all()
        return [Command(id=doc.doc_id, **doc) for doc in docs]

    def get_command(self, doc_id: int) -> Optional[Command]:
        doc = self.table.get(doc_id=doc_id)
        if doc:
            return Command(id=doc.doc_id, **doc)
        return None

    def get_command_by_text(self, text: str) -> Optional[Command]:
        doc = self.table.get(Query().text == text)
        if doc:
            return Command(id=doc.doc_id, **doc)
        return None

    def update_tally(self, doc_id: int):
        command = self.get_command(doc_id)
        if command:
            self.table.update(
                {"tally": command.tally + 1, "last_used": datetime.now().isoformat()},
                doc_ids=[doc_id]
            )

    def search_commands(self, query_str: str) -> List[Command]:
        query_str = query_str.lower()
        docs = self.table.search(
            (Query().text.test(lambda x: query_str in x.lower())) |
            (Query().description.test(lambda x: query_str in x.lower()))
        )
        return [Command(id=doc.doc_id, **doc) for doc in docs]

    def delete_command(self, doc_id: int):
        self.table.remove(doc_ids=[doc_id])
