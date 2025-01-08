
from datetime import datetime
from db.database import get_connection


class Tag:
    def __init__(self, id_, tree_id, tree_version_id, tag_name, description, created_at):
        self.id = id_
        self.tree_id = tree_id
        self.tree_version_id = tree_version_id
        self.tag_name = tag_name
        self.description = description
        self.created_at = created_at

    @classmethod
    def create(cls, tree_id: int, tree_version_id: int, tag_name: str, description: str="") -> "Tag":
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Tag (tree_id, tree_version_id, tag_name, description)
            VALUES (?, ?, ?, ?)
        """, (tree_id, tree_version_id, tag_name, description))
        conn.commit()
        return cls(cursor.lastrowid, tree_id, tree_version_id, tag_name, description, datetime.now())

    @classmethod
    def get_by_name(cls, tag_name: str) -> "Tag" :
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id,tree_id, tree_version_id, tag_name, description, created_at
            FROM Tag
            WHERE tag_name = ?
        """, (tag_name,))
        row = cursor.fetchone()
        if not row:
            return None
        return cls(row["id"], row["tree_id"], row["tree_version_id"], row["tag_name"], row["description"], row["created_at"])

    @classmethod
    def get_version_id_for_tag(cls, tag_name: str) -> int :
        """
        Helper method that returns just the version_id for a given tag_name (if not found).
        """
        t = cls.get_by_name(tag_name)
        if t:
            return t.tree_version_id
        return None

    def __repr__(self):
        return f"<Tag id={self.id},tree = {self.tree_id}, version={self.tree_version_id}, tag='{self.tag_name}'>"
