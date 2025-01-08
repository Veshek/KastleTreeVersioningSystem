from datetime import datetime
from db.database import get_connection
from src.Tag import Tag

class TreeVersion:
    def __init__(self, id_, tree_id, parent_version_id, created_at):
        self.id = id_
        self.tree_id = tree_id
        self.parent_version_id = parent_version_id
        self.created_at = created_at

    @classmethod
    def create(cls, tree_id: int, parent_version_id: int = None) -> "TreeVersion":
        """
        Create a new row in TreeVersion for the given Tree (tree_id),
        optionally referencing a parent_version_id for branching.
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO TreeVersion (tree_id, parent_version_id)
            VALUES (?, ?)
        """, (tree_id, parent_version_id))
        conn.commit()

        return cls(cursor.lastrowid, tree_id, parent_version_id, datetime.now())

    @classmethod
    def get(cls, version_id: int) -> "TreeVersion":
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, tree_id, parent_version_id, created_at
            FROM TreeVersion
            WHERE id = ?
        """, (version_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return cls(row["id"], row["tree_id"], row["parent_version_id"], row["created_at"])

    @classmethod
    def get_by_tag(cls, tag_name: str) -> "TreeVersion" :
        """
        Find which version the given tag references.
        """
        version_id = Tag.get_version_id_for_tag(tag_name)
        if version_id is None:
            return None
        return cls.get(version_id)

    def clone_from(self, parent_version_id: int):

        """
        Copy nodes/edges from parent_version_id into this version's ID.
        """
        conn = get_connection()
        cursor = conn.cursor()

        # 1) Copy Nodes
        cursor.execute("""
            SELECT id, data
            FROM TreeNode
            WHERE tree_version_id = ?
        """, (parent_version_id,))
        old_nodes = cursor.fetchall()

        old_to_new = {}
        for row in old_nodes:
            old_id = row["id"]
            data_json = row["data"]
            cursor.execute("""
                INSERT INTO TreeNode (tree_version_id, data)
                VALUES (?, ?)
            """, (self.id, data_json))
            conn.commit()
            new_id = cursor.lastrowid
            old_to_new[old_id] = new_id

        # 2) Copy Edges
        cursor.execute("""
            SELECT incoming_node_id, outgoing_node_id, data
            FROM TreeEdge
            WHERE tree_version_id = ?
        """, (parent_version_id,))
        old_edges = cursor.fetchall()

        for edge_row in old_edges:
            old_in = edge_row["incoming_node_id"]
            old_out = edge_row["outgoing_node_id"]
            edge_data = edge_row["data"]

            new_in = old_to_new[old_in]
            new_out = old_to_new[old_out]

            cursor.execute("""
                INSERT INTO TreeEdge (tree_version_id, incoming_node_id, outgoing_node_id, data)
                VALUES (?, ?, ?, ?)
            """, (self.id, new_in, new_out, edge_data))
        conn.commit()

    def delete_all_nodes_and_edges(self):
        """
        Delete all TreeNode and TreeEdge rows associated with this TreeVersion.
        Note: This permanently removes them from the database!
        """
        conn = get_connection() 
        cursor = conn.cursor()
        
        # 1) Delete edges that belong to this version
        cursor.execute("""
            DELETE FROM TreeEdge
            WHERE tree_version_id = ?
        """, (self.id,))
        
        # 2) Delete nodes that belong to this version
        cursor.execute("""
            DELETE FROM TreeNode
            WHERE tree_version_id = ?
        """, (self.id,))
        
        conn.commit()

    def __repr__(self):
        return (f"<TreeVersion id={self.id}, tree_id={self.tree_id}, "
                f"parent={self.parent_version_id}>")
