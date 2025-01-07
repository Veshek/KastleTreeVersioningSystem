from datetime import datetime
import json
from db.database import get_connection

conn = get_connection()

class TreeNode:
    def __init__(self, id_, tree_id, data, created_at):
        self.id = id_
        self.tree_id = tree_id
        self.data = data
        self.created_at = created_at

    @classmethod
    def create(cls, tree_id: int, data: dict) -> "TreeNode":
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO TreeNode (tree_id, data) VALUES (?, ?)",
            (tree_id, json.dumps(data))
        )
        conn.commit()
        return cls(cursor.lastrowid, tree_id, data, datetime.now())

    @classmethod
    def get(cls, node_id: int) -> "TreeNode" or None:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, tree_id, data, created_at FROM TreeNode WHERE id = ?",
            (node_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return cls(
            row["id"], row["tree_id"],
            json.loads(row["data"] or "{}"),
            row["created_at"]
        )

    def update_data(self, new_data: dict):
        cursor = conn.cursor()
        import json
        cursor.execute(
            "UPDATE TreeNode SET data = ? WHERE id = ?",
            (json.dumps(new_data), self.id)
        )
        conn.commit()
        self.data = new_data

    def delete(self):
        cursor = conn.cursor()
        cursor.execute("DELETE FROM TreeNode WHERE id = ?", (self.id,))
        conn.commit()

    def __repr__(self):
        return f"<TreeNode id={self.id}, tree_id={self.tree_id}, data={self.data}>"
