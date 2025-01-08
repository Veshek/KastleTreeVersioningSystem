import json
from datetime import datetime
from db.database import get_connection

class TreeEdge:
    def __init__(self, id_, tree_version_id, incoming_node_id, outgoing_node_id, data, created_at):
        self.id = id_
        self.tree_version_id = tree_version_id
        self.incoming_node_id = incoming_node_id
        self.outgoing_node_id = outgoing_node_id
        self.data = data
        self.created_at = created_at

    @classmethod
    def create(cls, tree_version_id: int, node_in: int, node_out: int, data: dict) -> "TreeEdge":
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO TreeEdge (tree_version_id, incoming_node_id, outgoing_node_id, data)
            VALUES (?, ?, ?, ?)
        """, (tree_version_id, node_in, node_out, json.dumps(data)))
        conn.commit()
        return cls(cursor.lastrowid, tree_version_id, node_in, node_out, data, datetime.now())

    @classmethod
    def get_for_node(cls, tree_version_id: int, node_id: int) -> list["TreeEdge"]:
        """
        Return edges where node_id is either incoming or outgoing in this version.
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, tree_version_id, incoming_node_id, outgoing_node_id, data, created_at
            FROM TreeEdge
            WHERE tree_version_id = ?
              AND (incoming_node_id = ? OR outgoing_node_id = ?)
        """, (tree_version_id, node_id, node_id))
        rows = cursor.fetchall()
        results = []
        for r in rows:
            data_dict = json.loads(r["data"] or "{}")
            results.append(cls(
                r["id"], r["tree_version_id"],
                r["incoming_node_id"], r["outgoing_node_id"],
                data_dict, r["created_at"]
            ))
        return results

    def __repr__(self):
        return (f"<TreeEdge id={self.id}, version={self.tree_version_id}, "
                f"in={self.incoming_node_id}, out={self.outgoing_node_id}, data={self.data}>")
