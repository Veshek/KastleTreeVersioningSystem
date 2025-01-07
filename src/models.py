import sqlite3
import json
from datetime import datetime
from db.database import get_connection
from collections import deque


##############################################################################
# TreeVersion Class
##############################################################################

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
    def get(cls, version_id: int) -> "TreeVersion" or None:
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
    def get_by_tag(cls, tag_name: str) -> "TreeVersion" or None:
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


##############################################################################
# Tag Class (Internal or Semi-Internal)
##############################################################################

class Tag:
    def __init__(self, id_, tree_version_id, tag_name, description, created_at):
        self.id = id_
        self.tree_version_id = tree_version_id
        self.tag_name = tag_name
        self.description = description
        self.created_at = created_at

    @classmethod
    def create(cls, tree_version_id: int, tag_name: str, description: str="") -> "Tag":
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Tag (tree_version_id, tag_name, description)
            VALUES (?, ?, ?)
        """, (tree_version_id, tag_name, description))
        conn.commit()
        return cls(cursor.lastrowid, tree_version_id, tag_name, description, datetime.now())

    @classmethod
    def get_by_name(cls, tag_name: str) -> "Tag" or None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, tree_version_id, tag_name, description, created_at
            FROM Tag
            WHERE tag_name = ?
        """, (tag_name,))
        row = cursor.fetchone()
        if not row:
            return None
        return cls(row["id"], row["tree_version_id"], row["tag_name"], row["description"], row["created_at"])

    @classmethod
    def get_version_id_for_tag(cls, tag_name: str) -> int or None:
        """
        Helper method that returns just the version_id for a given tag_name (or None if not found).
        """
        t = cls.get_by_name(tag_name)
        if t:
            return t.tree_version_id
        return None

    def __repr__(self):
        return f"<Tag id={self.id}, version={self.tree_version_id}, tag='{self.tag_name}'>"


##############################################################################
# TreeNode and TreeEdge (for any version)
##############################################################################

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
    def get(cls, node_id: int) -> "TreeNode" or None:
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


##############################################################################
# The Tree Class (Public Interface)
##############################################################################

class Tree:
    """
    A "Tree" object is the *public* interface for end-users.
    Internally, each Tree has multiple 'TreeVersion' rows. 
    The user does not see TreeVersion, Tag, etc. 
    The user only calls Tree methods: create_tag, create_new_tree_version_from_tag, etc.
    """

    def __init__(self, id_, name, created_at):
        self.id = id_
        self.name = name
        self.created_at = created_at
        # We create attributes working version and checpoint_version to keep track of changes and the last added tag
        self.working_version = None
        self.checkpoint_version = None

    @classmethod
    def create(cls, name: str) -> "Tree":
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Tree (name) VALUES (?)", (name,))
        conn.commit()
        return cls(cursor.lastrowid, name, datetime.now())

    @classmethod
    def get(cls, tree_id: int) -> "Tree":
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, created_at
            FROM Tree
            WHERE id = ?
        """, (tree_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return cls(row["id"], row["name"], row["created_at"])

    @classmethod
    def get_by_tag(cls, tag_name: str) -> "Tree":
        """
        Return a 'Tree' object referencing the version indicated by tag_name.
        
        We clear all the nodes and edges associated with the working version 
        and clone all the nodes and edges from the specified version, using the tag name
        """
        version = TreeVersion.get_by_tag(tag_name)
        if not version:
            return None
        base_tree = cls.get(version.tree_id)
        if not base_tree:
            return None
        # Store the version ID so we can do node/edge ops
        base_tree.checkpoint_version = version
        base_tree.working_version = base_tree.create_new_version()
        base_tree.working_version.clone_from(base_tree.checkpoint_version.id)
        return base_tree

    def create_new_version(self, parent_version_id: int = None) -> int:
        """
        Create a brand new TreeVersion row, referencing parent_version_id if given.
        Return the new version's ID.
        """
        new_version = TreeVersion.create(self.id, parent_version_id)
        return new_version

    def create_tag(self, tag_name: str, description: str = "") -> "Tag":
        """
        Clone the working version into a new version
        Link the New Version to a tag 
        Reference the Checkpoint Version as Parent of new Version
        Set New Version as the new Checkpoint 
        """
        if not self.working_version:
            self.working_version = self.create_new_version()
        if not self.checkpoint_version:
            self.checkpoint_version = self.create_new_version()

        new_version = self.create_new_version(self.checkpoint_version.id)
        new_version.clone_from(self.working_version.id)
        self.checkpoint_version = new_version

        return Tag.create(new_version.id, tag_name, description)

    def create_new_tree_version_from_tag(self, tag_name: str) -> "Tree":
        """
        1. Find the TreeVersion for tag_name.
        2. Set the checkpoint_version to this Version
        3. Create a New working version 
        4. Clone all changes 
        """
        parent_version = TreeVersion.get_by_tag(tag_name)
        if not parent_version:
            raise ValueError(f"No tag '{tag_name}' found.")

        # Return a new Tree object that references this new version
        new_tree = Tree(self.id, self.name, self.created_at)
        new_tree.working_version = self.create_new_version()
        new_tree.working_version.clone_from(parent_version.id)
        new_tree.checkpoint_version = parent_version
        return new_tree

    def restore_from_tag(self, tag_name: str) -> "Tree":
        """
        "Rollback": just like create_new_tree_version_from_tag,
        we produce a new version cloned from the old tagged version.
        """
        return self.create_new_tree_version_from_tag(tag_name)

    # ------------------------------------------------------------------
    # Node & Edge Operations
    # ------------------------------------------------------------------

    def get_all_nodes(self):
        """
        Returns a list of TreeNode objects that belong to this Tree (version).
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, tree_version_id, data, created_at FROM TreeNode WHERE tree_version_id = ?",
            (self.working_version.id,)
        )
        rows = cursor.fetchall()
        nodes = []
        for r in rows:
            data_dict = json.loads(r["data"] or "{}")
            nodes.append(TreeNode(r["id"], r["tree_version_id"], data_dict, r["created_at"]))
        return nodes

    def get_all_edges(self):
        """
        Returns a list of TreeEdge objects that belong to this Tree (version).
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, tree_version_id, incoming_node_id, outgoing_node_id, data, created_at "
            "FROM TreeEdge WHERE tree_version_id = ?",
            (self.working_version.id,)
        )
        rows = cursor.fetchall()
        edges = []
        for r in rows:
            data_dict = json.loads(r["data"] or "{}")
            edges.append(
                TreeEdge(
                    r["id"],
                    r["tree_version_id"],
                    r["incoming_node_id"],
                    r["outgoing_node_id"],
                    data_dict,
                    r["created_at"]
                )
            )
        return edges

    def add_node(self, data: dict) -> TreeNode:
        if not self.working_version.id:
            # No current version? Create one quickly
            self.working_version.id = self.create_new_version()
        return TreeNode.create(self.working_version.id, data)

    def add_edge(self, node_id_1: int, node_id_2: int, data: dict) -> TreeEdge:
        if not self.working_version.id:
            self.working_version.id = self.create_new_version()
        return TreeEdge.create(self.working_version.id, node_id_1, node_id_2, data)

    def get_node(self, node_id: int) -> TreeNode:
        return TreeNode.get(node_id)

    def get_node_edges(self, node_id: int) -> list[TreeEdge]:
        if not self.working_version.id:
            raise ValueError("Tree has no current version to reference edges.")
        return TreeEdge.get_for_node(self.working_version.id, node_id)

    def get_child_nodes(self, node_id: int) -> list[TreeNode]:
        if not self.working_version.id:
            raise ValueError("Tree has no current version for child lookup.")
        return TreeNode.get_children(self.working_version.id, node_id)

    def get_parent_nodes(self, node_id: int) -> list[TreeNode]:
        if not self.working_version.id:
            raise ValueError("Tree has no current version for parent lookup.")
        return TreeNode.get_parents(self.working_version.id, node_id)

    def get_root_nodes(self) -> list[TreeNode]:
        if not self.working_version.id:
            raise ValueError("Tree has no current version for root lookup.")
        return TreeNode.get_roots(self.working_version.id)

    def get_nodes_at_depth(self, depth: int) -> list[TreeNode]:
        if not self.working_version.id:
            raise ValueError("Tree has no current version for depth lookup.")
        if depth < 0:
            return []

        queue = deque([(n.id, 0) for n in self.get_root_nodes()])
        results = []
        visited = set()

        while queue:
            nid, lvl = queue.popleft()
            if nid in visited:
                continue
            visited.add(nid)

            if lvl == depth:
                node_obj = self.get_node(nid)
                if node_obj:
                    results.append(node_obj)
            elif lvl < depth:
                children = self.get_child_nodes(nid)
                for c in children:
                    queue.append((c.id, lvl + 1))
        return results

    def find_path(self, start_node_id: int, end_node_id: int) -> list[tuple[TreeNode, TreeEdge]]:
        """
        BFS to find a path from start_node_id to end_node_id.
        Return list of (TreeNode, TreeEdge) pairs.
        """
        if not self.working_version.id:
            raise ValueError("Tree has no current version for pathfinding.")

        start_node = self.get_node(start_node_id)
        if not start_node:
            return []

        queue = deque([(start_node, [])])
        visited = set([start_node_id])

        while queue:
            current_node, path_so_far = queue.popleft()
            if current_node.id == end_node_id:
                return path_so_far + [(current_node, None)]

            edges = self.get_node_edges(current_node.id)
            for e in edges:
                if e.incoming_node_id == current_node.id:
                    nxt = e.outgoing_node_id
                    if nxt not in visited:
                        visited.add(nxt)
                        next_node = self.get_node(nxt)
                        new_path = path_so_far + [(current_node, e)]
                        queue.append((next_node, new_path))
        return []

    def __repr__(self):
        vid = getattr(self, "working_version.id", None)
        return f"<Tree id={self.id}, name='{self.name}', working_version={vid}>"

##############################################################################
# End of single-file example
##############################################################################
