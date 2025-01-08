import json
from datetime import datetime
from db.database import get_connection
from collections import deque

class TreeNode:
    def __init__(self, id_, tree_version_id, data, created_at):
        self.id = id_
        self.tree_version_id = tree_version_id
        self.data = data
        self.created_at = created_at

    @classmethod
    def create(cls, tree_version_id: int, data: dict) -> "TreeNode":
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO TreeNode (tree_version_id, data)
            VALUES (?, ?)
        """, (tree_version_id, json.dumps(data)))
        conn.commit()
        return cls(cursor.lastrowid, tree_version_id, data, datetime.now())

    @classmethod
    def get(cls, node_id: int) -> "TreeNode" :
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, tree_version_id, data, created_at
            FROM TreeNode
            WHERE id = ?
        """, (node_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return cls(
            row["id"],
            row["tree_version_id"],
            json.loads(row["data"] or "{}"),
            row["created_at"]
        )

    @classmethod
    def get_children(cls, tree_version_id: int, node_id: int) -> list["TreeNode"]:
        """
        Return direct children where node_id is the 'incoming_node_id'.
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT n.id, n.tree_version_id, n.data, n.created_at
            FROM TreeNode n
            JOIN TreeEdge e ON e.outgoing_node_id = n.id
            WHERE n.tree_version_id = ?
              AND e.tree_version_id = ?
              AND e.incoming_node_id = ?
        """, (tree_version_id, tree_version_id, node_id))
        rows = cursor.fetchall()
        results = []
        for r in rows:
            results.append(cls(
                r["id"], r["tree_version_id"],
                json.loads(r["data"] or "{}"),
                r["created_at"]
            ))
        return results

    @classmethod
    def get_parents(cls, tree_version_id: int, node_id: int) -> list["TreeNode"]:
        """
        Return direct parents where node_id is the 'outgoing_node_id'.
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT n.id, n.tree_version_id, n.data, n.created_at
            FROM TreeNode n
            JOIN TreeEdge e ON e.incoming_node_id = n.id
            WHERE n.tree_version_id = ?
              AND e.tree_version_id = ?
              AND e.outgoing_node_id = ?
        """, (tree_version_id, tree_version_id, node_id))
        rows = cursor.fetchall()
        results = []
        for r in rows:
            results.append(cls(
                r["id"], r["tree_version_id"],
                json.loads(r["data"] or "{}"),
                r["created_at"]
            ))
        return results

    @classmethod
    def get_roots(cls, tree_version_id: int) -> list["TreeNode"]:
        """
        Return nodes that have no incoming edge in this version.
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT n.id, n.tree_version_id, n.data, n.created_at
            FROM TreeNode n
            WHERE n.tree_version_id = ?
              AND n.id NOT IN (
                SELECT outgoing_node_id
                FROM TreeEdge
                WHERE tree_version_id = ?
              )
        """, (tree_version_id, tree_version_id))
        rows = cursor.fetchall()
        results = []
        for r in rows:
            results.append(cls(
                r["id"], r["tree_version_id"],
                json.loads(r["data"] or "{}"),
                r["created_at"]
            ))
        return results


    def __repr__(self):
        return (f"<TreeNode id={self.id}, version={self.tree_version_id}, "
                f"data={self.data}>")
