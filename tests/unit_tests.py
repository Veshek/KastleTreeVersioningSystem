import pytest
from src.Tree import Tree
from src.TreeVersion import TreeVersion
from src.Tag import Tag
from src.TreeNode import TreeNode
from db.database import get_connection, initialize_db

@pytest.fixture(scope="function")
def db_conn():
    conn = get_connection()
    initialize_db(conn)
    yield conn
    conn.close()


def test_create_tree(db_conn):
    Tree.create("MyTestTree")
    tree = Tree.get(tree_id=1)
    assert tree.id is not None
    assert tree.name == "MyTestTree"
    assert tree.checkpoint_version is None


def test_get_tree(db_conn):
    tree = Tree.create("ExistingTree")
    fetched_tree = Tree.get(tree.id)
    assert fetched_tree is not None
    assert fetched_tree.id == tree.id
    assert fetched_tree.name == "ExistingTree"


def test_create_tag(db_conn):
    Tree.create("TagTree")
    tree = Tree.get(tree_id=1)

    tag = tree.create_tag("v1.0", "Initial Release")

    assert tag is not None
    assert tag.tag_name == "v1.0"
    assert tag.tree_version_id == tree.checkpoint_version.id

    fetched_tag = Tag.get_by_name("v1.0")
    assert fetched_tag is not None
    assert fetched_tag.description == "Initial Release"


def test_add_node(db_conn):
    Tree.create("NodeTestTree")
    tree = Tree.get(tree_id=1)
    node_data = {"key": "value"}
    node = tree.add_node(node_data)

    assert node is not None
    assert node.tree_version_id == tree.working_version.id
    assert node.data == node_data


def test_add_edge(db_conn):
    Tree.create("EdgeTestTree")
    tree = Tree.get(tree_id=1)
    node1 = tree.add_node({"key": "node1"})
    node2 = tree.add_node({"key": "node2"})

    edge = tree.add_edge(node1.id, node2.id, {"relation": "connected"})
    assert edge is not None
    assert edge.incoming_node_id == node1.id
    assert edge.outgoing_node_id == node2.id
    assert edge.tree_version_id == tree.working_version.id


def test_get_by_tag(db_conn):
    Tree.create("TaggableTree")
    tree = Tree.get(tree_id=1)
    tree.create_tag("v1.1", "First checkpoint")
    fetched_tree = Tree.get_by_tag("v1.1")

    assert fetched_tree is not None
    assert fetched_tree.checkpoint_version is not None
    assert fetched_tree.working_version is not None


def test_restore_from_tag(db_conn):
    Tree.create("RollbackTree")
    tree = Tree.get(tree_id=1)
    tree.create_tag("stable-v1", "Stable checkpoint")
    node1 = tree.add_node({"key": "experimental"})
    tree.create_tag("exp-v1", "Experimental tag")

    rollback_tree = tree.restore_from_tag("stable-v1")
    assert rollback_tree is not None
    assert rollback_tree.checkpoint_version.id == Tag.get_version_id_for_tag("stable-v1")
    assert len(rollback_tree.get_all_nodes()) == 0  # Experimental node should not exist


def test_clone_version(db_conn):
    Tree.create("CloneTree")
    tree = Tree.get(tree_id=1)
    node1 = tree.add_node({"key": "original_node"})
    tree.create_tag("v1", "Baseline")
    node2 = tree.add_node({"key": "clone_node"})

    cloned_tree = tree.create_new_tree_version_from_tag("v1")
    assert cloned_tree is not None
    assert len(cloned_tree.get_all_nodes()) == 1  # Node cloned from baseline


def test_tag_creation_on_new_version(db_conn):
    Tree.create("TagVersionTree")
    tree = Tree.get(tree_id=1)
    tree.create_tag("v1.0")
    tree.add_node({"setting": "new_value"})
    tree.create_tag("v1.1")

    assert tree.checkpoint_version is not None
    assert tree.checkpoint_version.id != tree.working_version.id


def test_pathfinding(db_conn):
    Tree.create("PathTree")
    tree = Tree.get(tree_id=1)
    node1 = tree.add_node({"node": "A"})
    node2 = tree.add_node({"node": "B"})
    node3 = tree.add_node({"node": "C"})

    tree.add_edge(node1.id, node2.id, {"weight": 5})
    tree.add_edge(node2.id, node3.id, {"weight": 10})

    path = tree.find_path(node1.id, node3.id)
    assert len(path) == 3
    assert path[0][0].data == {"node": "A"}
    assert path[1][0].data == {"node": "B"}
    assert path[2][0].data == {"node": "C"}
