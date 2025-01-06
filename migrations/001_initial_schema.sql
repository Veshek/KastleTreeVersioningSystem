CREATE TABLE IF NOT EXISTS Tree (
id INTEGER PRIMARY KEY,
name TEXT NOT NULL,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS TreeNode(
id INTEGER PRIMARY KEY,
tree_id INTEGER NOT NULL,
data JSON, -- Stores node-specific data
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (tree_id) REFERENCES Tree(id)
);

CREATE TABLE IF NOT EXISTS TreeEdge(
id INTEGER PRIMARY KEY,
incoming_node_id INTEGER NOT NULL,  -- origin node for this edge
outgoing_node_id INTEGER NOT NULL, -- destination node for this edge
data JSON, -- Stores edge-specific metadata
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (incoming_node_id) REFERENCES TreeNode(id),
FOREIGN KEY (outgoing_node_id) REFERENCES TreeNode(id)
);