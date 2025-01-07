BEGIN TRANSACTION;

DROP TABLE IF EXISTS Tree;
DROP TABLE IF EXISTS TreeVersion;
DROP TABLE IF EXISTS Tag;
DROP TABLE IF EXISTS TreeNode;
DROP TABLE IF EXISTS TreeEdge;

-- ========== 1) Tree ==========
-- A "logical" tree (project/config).
-- e.g., "MyApp" or "Configuration A"
CREATE TABLE IF NOT EXISTS Tree (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========== 2) TreeVersion ==========
-- Each row represents a *snapshot* version of a particular Tree.
-- parent_version_id helps track lineage/branching.
CREATE TABLE IF NOT EXISTS TreeVersion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tree_id INTEGER NOT NULL,
    parent_version_id INTEGER,  -- points to another TreeVersion row if branching
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (tree_id) REFERENCES Tree(id),
    FOREIGN KEY (parent_version_id) REFERENCES TreeVersion(id)
);

-- ========== 3) Tag ==========
-- Each Tag references exactly one TreeVersion.
-- e.g. tag_name="release-v1.0" or "stable-2025-01-01"
CREATE TABLE IF NOT EXISTS Tag (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tree_version_id INTEGER NOT NULL,
    tree_id INTEGER NOT NULL,
    tag_name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (tree_version_id) REFERENCES TreeVersion(id),
    FOREIGN KEY (tree_id) REFERENCES Tree(id),

    -- Enforce that (tree_id, tag_name) is unique
    UNIQUE (tree_id, tag_name)
);

-- ========== 4) TreeNode ==========
-- Each version has its own set of nodes (snapshot-based).
CREATE TABLE IF NOT EXISTS TreeNode (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tree_version_id INTEGER NOT NULL,
    data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (tree_version_id) REFERENCES TreeVersion(id)
);

-- ========== 5) TreeEdge ==========
-- Each version has its own set of edges.
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

COMMIT;
