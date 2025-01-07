from datetime import datetime
from src.TreeNode import TreeNode
from src.TreeEdge import TreeEdge
from src.Tag import Tag 
import json

# Import the global connection from your database module
from db.database import get_connection
conn = get_connection()

class Tree:
    def __init__(self, id_, name, parent_id, created_at):
        self.id = id_
        self.name = name
        self.parent_id = parent_id
        self.created_at = created_at

    @classmethod
    def create(cls, name: str, parent_id: int = None) -> "Tree":
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Tree (name, parent_id) VALUES (?, ?)",
            (name, parent_id)
        )
        conn.commit()
        return cls(cursor.lastrowid, name, parent_id, datetime.now())

    @classmethod
    def get(cls, tree_id: int) -> "Tree" or None:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, parent_id, created_at FROM Tree WHERE id = ?",
            (tree_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return cls(row["id"], row["name"], row["parent_id"], row["created_at"])

    def create_tag(self, tag_name: str, description: str = "") -> "Tag":
        """
        Creates a brand-new "snapshot" (row in Tree), copies over
        all nodes & edges from this tree, and then creates a Tag
        pointing to that new snapshot.
        
        This ensures the tag references an immutable version, 
        unaffected by future edits to the 'current' tree.
        """
        # 1) Clone ourselves into a new Tree row
        cloned_tree = Tree.create(
            name=f"{self.name}-{tag_name}", 
            parent_id=self.id
        )

        # 2) Copy nodes and edges (from self.id to cloned_tree.id)
        self._clone_nodes_and_edges(from_tree_id=self.id, to_tree_id=cloned_tree.id)

        # 3) Create a Tag referencing the cloned_tree
        new_tag = Tag.create(
            tree_id=cloned_tree.id, 
            tag_name=tag_name, 
            description=description
        )
        return new_tag

    @classmethod
    def get_by_tag(cls, tag_name: str) -> "Tree" or None:
        """
        Find which Tree row is referenced by tag_name, then return that Tree object.
        """
        t = Tag.get_by_name(tag_name)
        if t is None:
            return None
        return cls.get(t.tree_id)

    def create_new_tree_version_from_tag(self, tag_name: str) -> "Tree":
        """
        1. Find the Tree that 'tag_name' references.
        2. Create a new Tree row referencing that parent's ID.
        3. Copy all nodes/edges from the parent version to the new one.
        4. Return the new Tree instance.
        """
        parent_tree = Tree.get_by_tag(tag_name)
        if parent_tree is None:
            raise ValueError(f"No tag '{tag_name}' found.")

        # Create new row
        new_tree = Tree.create(name=f"Derived from {tag_name}", parent_id=parent_tree.id)

        # Copy parent nodes/edges
        self._clone_nodes_and_edges(from_tree_id=parent_tree.id, to_tree_id=new_tree.id)

        return new_tree

    def restore_from_tag(self, tag_name: str) -> "Tree":
        """
        Rollback by creating a new version cloned from an older tagged version.
        """
        return self.create_new_tree_version_from_tag(tag_name)

    def _clone_nodes_and_edges(self, from_tree_id: int, to_tree_id: int):
        """
        Copy nodes and edges from one tree_id to another. Requires a node ID mapping.
        """
        cursor = conn.cursor()

        # 1) Copy nodes
        cursor.execute("SELECT id, data FROM TreeNode WHERE tree_id = ?", (from_tree_id,))
        old_nodes = cursor.fetchall()
        old_to_new = {}
        for row in old_nodes:
            old_id = row["id"]
            data_json = row["data"]
            cursor.execute(
                "INSERT INTO TreeNode (tree_id, data) VALUES (?, ?)",
                (to_tree_id, data_json)
            )
            conn.commit()
            new_id = cursor.lastrowid
            old_to_new[old_id] = new_id

        # 2) Copy edges
        cursor.execute("SELECT incoming_node_id, outgoing_node_id, data FROM TreeEdge WHERE tree_id = ?", (from_tree_id,))
        old_edges = cursor.fetchall()
        for e in old_edges:
            in_id = old_to_new[e["incoming_node_id"]]
            out_id = old_to_new[e["outgoing_node_id"]]
            data_json = e["data"]
            cursor.execute(
                "INSERT INTO TreeEdge (tree_id, incoming_node_id, outgoing_node_id, data) "
                "VALUES (?, ?, ?, ?)",
                (to_tree_id, in_id, out_id, data_json)
            )
        conn.commit()

    # Node & Edge convenience methods
    def add_node(self, data: dict) -> "TreeNode":
        return TreeNode.create(self.id, data)

    def add_edge(self, node_id_1: int, node_id_2: int, data: dict) -> "TreeEdge":
        return TreeEdge.create(self.id, node_id_1, node_id_2, data)

    def get_node(self, node_id: int):
        node = TreeNode.get(node_id)
        return node  # optionally check node.tree_id == self.id if needed

    def get_root_nodes(self):
        """
        Return nodes that are not listed as an 'outgoing_node_id' in TreeEdge.
        """
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, data, created_at
            FROM TreeNode
            WHERE tree_id = ?
              AND id NOT IN (
                SELECT outgoing_node_id FROM TreeEdge WHERE tree_id = ?
              )
            """,
            (self.id, self.id)
        )
        rows = cursor.fetchall()
        results = []
        for r in rows:
            results.append(TreeNode(r["id"], self.id, json.loads(r["data"] or "{}"), r["created_at"]))
        return results

    def __repr__(self):
        return f"<Tree id={self.id}, name={self.name}, parent_id={self.parent_id}>"

