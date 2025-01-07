# tag.py
from datetime import datetime
from db.database import get_connection

conn = get_connection()

class Tag:
    def __init__(self, id_, tree_id, tag_name, description, created_at):
        self.id = id_
        self.tree_id = tree_id
        self.tag_name = tag_name
        self.description = description
        self.created_at = created_at

    @classmethod
    def create(cls, tree_id: int, tag_name: str, description: str = "") -> "Tag":
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Tag (tree_id, tag_name, description) VALUES (?, ?, ?)",
            (tree_id, tag_name, description)
        )
        conn.commit()
        return cls(cursor.lastrowid, tree_id, tag_name, description, datetime.now())

    @classmethod
    def get_by_name(cls, tag_name: str) -> "Tag" or None:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, tree_id, tag_name, description, created_at FROM Tag WHERE tag_name = ?",
            (tag_name,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return cls(row["id"], row["tree_id"], row["tag_name"], row["description"], row["created_at"])

    def __repr__(self):
        return f"<Tag id={self.id}, tree_id={self.tree_id}, tag_name='{self.tag_name}'>"
