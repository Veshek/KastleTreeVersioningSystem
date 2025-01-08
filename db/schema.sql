BEGIN TRANSACTION;

DROP TABLE IF EXISTS Tree;
DROP TABLE IF EXISTS TreeVersion;
DROP TABLE IF EXISTS Tag;
DROP TABLE IF EXISTS TreeNode;
DROP TABLE IF EXISTS TreeEdge;

-- ========== 1) Tree ==========
CREATE TABLE IF NOT EXISTS Tree (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========== 2) TreeVersion ==========
CREATE TABLE IF NOT EXISTS TreeVersion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tree_id INTEGER NOT NULL,
    parent_version_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (tree_id) REFERENCES Tree(id),
    FOREIGN KEY (parent_version_id) REFERENCES TreeVersion(id)
);

-- Add index on TreeVersion.id
CREATE INDEX idx_treeversion_id ON TreeVersion(id);

-- ========== 3) Tag ==========
CREATE TABLE IF NOT EXISTS Tag (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tree_version_id INTEGER NOT NULL,
    tree_id INTEGER NOT NULL,
    tag_name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (tree_version_id) REFERENCES TreeVersion(id),
    FOREIGN KEY (tree_id) REFERENCES Tree(id),

    UNIQUE (tree_id, tag_name)
);

-- Add index on Tag.tag_name
CREATE INDEX idx_tag_name ON Tag(tag_name);


-- ========== 4) TreeNode ==========
CREATE TABLE IF NOT EXISTS TreeNode (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tree_version_id INTEGER NOT NULL,
    data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (tree_version_id) REFERENCES TreeVersion(id)
);

-- Add index on TreeNode.tree_version_id
CREATE INDEX idx_treenode_tree_version_id ON TreeNode(tree_version_id);

-- ========== 5) TreeEdge ==========
CREATE TABLE IF NOT EXISTS TreeEdge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tree_version_id INTEGER NOT NULL,
    incoming_node_id INTEGER NOT NULL,
    outgoing_node_id INTEGER NOT NULL,
    data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (tree_version_id) REFERENCES TreeVersion(id),
    FOREIGN KEY (incoming_node_id) REFERENCES TreeNode(id),
    FOREIGN KEY (outgoing_node_id) REFERENCES TreeNode(id)
);

-- Add index on TreeEdge.tree_version_id
CREATE INDEX idx_treeedge_tree_version_id ON TreeEdge(tree_version_id);

COMMIT;
