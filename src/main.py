from db.database import get_connection, initialize_db
from src.Tree import Tree
from src.TreeVersion import TreeVersion 
from src.Tag import Tag
from src.TreeNode import TreeNode
from src.TreeEdge import TreeEdge

def main():
     # 1) Initialize the database (run migrations)
    conn = get_connection()
    initialize_db(conn)  # creates tables if not exist
    conn.close()

    # 1) Create a Tree
    Tree.create('My Configuration')
    tree = Tree.get(tree_id=1)
    new_tag = tree.create_tag("release-v1.0", description="Initial stable release")
    # Making changes to the configuration
    modified_tree =  tree.create_new_tree_version_from_tag("release-v1.0")
    new_node = modified_tree.add_node(data={"setting": "new_value"})
    modified_tree.create_tag("release-v1.1", description="Added new setting")
    # Adding an edge between nodes
    modified_tree.add_edge(node_id_1=1, node_id_2=2, data={"weight": 0.5})
    
    rollback_tree = Tree.get_by_tag('release-v1.1')
    print(rollback_tree.get_all_edges())
    print(rollback_tree.get_all_nodes())

    print(modified_tree.get_all_edges())
    print(modified_tree.get_all_nodes())


    proceed = input("continue? 7")
    # 6) Feature Branching
    main_tree = Tree.get_by_tag("main-v2.0")
    if main_tree:
        feature_branch = main_tree.create_new_tree_version_from_tag("main-v2.0")
        node1 = feature_branch.add_node({"feature_flag": True})
        node2 = feature_branch.add_node({"config": "new_setting"})
        feature_branch.add_edge(node1.id, node2.id, {"relation": "depends_on"})
        feature_branch.create_tag("feature-x-v1", "Feature X implementation")

    proceed = input("continue? 8")
    # 7) Rollback
    stable_tree = Tree.get(1)
    stable_tree.create_tag("stable-v1")
    new_node = stable_tree.add_node({"experimental": True})
    stable_tree.add_edge(1, new_node.id, {"type": "experimental"})
    if problems_detected():
        rollback_tree = stable_tree.restore_from_tag("stable-v1")

    proceed = input("continue? 9")
    # 8) Traversal
    historical_tree = Tree.get_by_tag("release-v1.0")
    if historical_tree:
        root_nodes = historical_tree.get_root_nodes()
        for root in root_nodes:
            traverse_tree(historical_tree, root.id)

def traverse_tree(tree_obj: Tree, node_id: int):
    node = tree_obj.get_node(node_id)
    print(f"Node {node_id} data: {node.data}")
    edges = tree_obj.get_node_edges(node_id)
    for e in edges:
        if e.incoming_node_id == node_id:
            print(f"Edge {e.id} => data: {e.data}")
            traverse_tree(tree_obj, e.outgoing_node_id)

def problems_detected():
    return False

if __name__ == "__main__":
    main()
