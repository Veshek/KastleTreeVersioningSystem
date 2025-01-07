from datetime import datetime
import json
from db.database import get_connection
conn = get_connection()

class TreeEdge:
    def __init__(self, id_, tree_id, incoming_node_id, outgoing_node_id, data, created_at):
        self.id = id_
        self.tree_id = tree_id
        self.incoming_node_id = incoming_node_id
        self.outgoing_node_id = outgoing_node_id
        self.data = data
        self.created_at = created_at

    @classmethod
    def create(cls, tree_id: int, node_in: int, node_out: int, data: dict) -> "TreeEdge":
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO TreeEdge (tree_id, incoming_node_id, outgoing_node_id, data)
            VALUES (?, ?, ?, ?)
            """,
            (tree_id, node_in, node_out, json.dumps(data))
        )
        conn.commit()
        return cls(cursor.lastrowid, tree_id, node_in, node_out, data, datetime.now())

    @classmethod
    def get_for_node(cls, tree_id: int, node_id: int) -> list["TreeEdge"]:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, tree_id, incoming_node_id, outgoing_node_id, data, created_at
            FROM TreeEdge
            WHERE tree_id = ?
              AND (incoming_node_id = ? OR outgoing_node_id = ?)
            """,
            (tree_id, node_id, node_id)
        )
        rows = cursor.fetchall()
        edges = []
        for row in rows:
            data_dict = json.loads(row["data"] or "{}")
            edges.append(
                cls(row["id"], row["tree_id"], row["incoming_node_id"], 
                    row["outgoing_node_id"], data_dict, row["created_at"])
            )
        return edges

    def update_data(self, new_data: dict):
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE TreeEdge SET data = ? WHERE id = ?",
            (json.dumps(new_data), self.id)
        )
        conn.commit()
        self.data = new_data

    def delete(self):
        cursor = conn.cursor()
        cursor.execute("DELETE FROM TreeEdge WHERE id = ?", (self.id,))
        conn.commit()

    def __repr__(self):
        return (f"<TreeEdge id={self.id}, tree_id={self.tree_id}, "
                f"in={self.incoming_node_id}, out={self.outgoing_node_id}, data={self.data}>")
