CREATE TABLE IF NOT EXISTS Tree (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL,
parent_id INTEGER,  -- points to another row in Tree (the 'version' we branched from)
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (parent_id) REFERENCES Tree(id)
);

CREATE TABLE IF NOT EXISTS TreeNode (
id INTEGER PRIMARY KEY AUTOINCREMENT,
tree_id INTEGER NOT NULL,   -- points to the row in Tree
data JSON,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (tree_id) REFERENCES Tree(id)
);

CREATE TABLE IF NOT EXISTS TreeEdge (
id INTEGER PRIMARY KEY AUTOINCREMENT,
tree_id INTEGER NOT NULL,   -- points to the row in Tree
incoming_node_id INTEGER NOT NULL,
outgoing_node_id INTEGER NOT NULL,
data JSON,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (tree_id) REFERENCES Tree(id),
FOREIGN KEY (incoming_node_id) REFERENCES TreeNode(id),
FOREIGN KEY (outgoing_node_id) REFERENCES TreeNode(id)
);

CREATE TABLE IF NOT EXISTS Tag (
id INTEGER PRIMARY KEY AUTOINCREMENT,
tree_id INTEGER NOT NULL,   -- each tag references exactly one row in Tree
tag_name TEXT NOT NULL,
description TEXT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (tree_id) REFERENCES Tree(id)
);
