import pytest
import os
from db.database import get_connection, initialize_db
from src.Tree import Tree

"""
!! NOTE !!
All the tests compare the number of nodes and edges that are expected to be returned by
specific versions of trees. Element wise comparision is not possible as python equality
compares references to the same object and doesn't actually check if the content of the objects
are the same. 

"""

@pytest.fixture(scope="function")
def db_conn():
    print('here')
    conn = get_connection()
    initialize_db(conn)
    yield conn
    conn.close()

def test_restore_and_tagging(db_conn):
    """
    Testing restore_by_tag, create_tag and create_new_tree_version_from_tag

    We check if the restore_by_tag function works by checking that the Tree object returned has the 
    the appropriate number of nodes

    1. when copying a tag with an empty tree we expect 0 nodes
    2. when copying a tag with a tree with 2 nodes and 1 edge we should get 2 two nodes and 1 edge
    """
    Tree.create('My Configuration')
    tree = Tree.get(tree_id=1)
    new_tag = tree.create_tag("release-v1.0", description="Empty Tree")
    # Making changes to the configuration
    modified_tree =  tree.create_new_tree_version_from_tag("release-v1.0")
    node1 = modified_tree.add_node(data={"node1": "val1"})
    node2 = modified_tree.add_node(data={"node2": "val2"})

    modified_tree.add_edge(node1.id,node2.id,data = {'edge1':0})
    modified_tree.create_tag("release-v1.1", description="Added new setting")
    # Adding an edge between nodes
    rollback_tree_expect_empty = modified_tree.restore_from_tag("release-v1.0")
    rollback_tree_expect_non_empty = modified_tree.restore_from_tag("release-v1.1")

    assert len(rollback_tree_expect_empty.get_all_nodes()) == 0
    assert len(rollback_tree_expect_non_empty.get_all_nodes()) == 2
    assert len(rollback_tree_expect_non_empty.get_all_edges()) == 1
    
def test_level_depth_traversal(db_conn):
    """
    Test if the get_nodes_at_depth function yields the appropriate nodes  

    We will call the function to find all nodes at level1. We should expect to get 4 nodes  

        Level0                node1               node2
                             //    \\            //    \\
                            //      \\          //      \\
                           vv        vv        vv        vv
        Level1            node3      node4    node5      node6
                         //
                        //
                       vv
        Level2        node7

    """
    Tree.create('My Configuration')
    tree = Tree.get(tree_id=1)
    new_tag = tree.create_tag("release-v1.0", description="Empty Tree")

    node1 = tree.add_node(data={"node1":"val1"})
    node2 = tree.add_node(data={"node2":"val2"})
    node3 = tree.add_node(data={"node3":"val3"})
    node4 = tree.add_node(data={"node4":"val4"})
    node5 = tree.add_node(data={"node5":"val5"})
    node6 = tree.add_node(data={"node6":"val6"})
    node7 = tree.add_node(data={"node7":"val7"})

    tree.add_edge(node1.id,node3.id,data={"1-3":"0"})
    tree.add_edge(node1.id,node4.id,data={"1-4":"0"})
    tree.add_edge(node2.id,node5.id,data={"2-5":"0"})
    tree.add_edge(node2.id,node6.id,data={"2-6":"0"})
    tree.add_edge(node3.id,node7.id,data={"3-7":"0"})

    assert  len(tree.get_root_nodes()) == 2
    result = tree.get_nodes_at_depth(1)
    assert len(result) == 4

def test_pathfinding(db_conn):
    """
    Test if the get_nodes_at_depth function yields the appropriate nodes  

    We will call the function to find all nodes at level1. We should expect to get 4 nodes  

        Level0                node1                 node2
                             ^^    \\              //    \\
                            //      \\            //      \\
                           //        vv           vv       vv
        Level1            node3      node4 ====> node5     node6
                         //
                        //
                       vv
        Level2         node7

    """
    Tree.create('My Configuration')
    tree = Tree.get(tree_id=1)
    new_tag = tree.create_tag("release-v1.0", description="Empty Tree")

    node1 = tree.add_node(data={"node1":"val1"})
    node2 = tree.add_node(data={"node2":"val2"})
    node3 = tree.add_node(data={"node3":"val3"})
    node4 = tree.add_node(data={"node4":"val4"})
    node5 = tree.add_node(data={"node5":"val5"})
    node6 = tree.add_node(data={"node6":"val6"})
    node7 = tree.add_node(data={"node7":"val7"})

    edge3_1=tree.add_edge(node3.id,node1.id,data={"3-1":"0"})
    edge1_4=tree.add_edge(node1.id,node4.id,data={"1-4":"0"})
    edge4_5=tree.add_edge(node4.id,node5.id,data={"4-5":"0"})
    edge2_5=tree.add_edge(node2.id,node5.id,data={"2-5":"0"})
    edge2_6=tree.add_edge(node2.id,node6.id,data={"2-6":"0"})
    edge3_7=tree.add_edge(node3.id,node7.id,data={"3-7":"0"})

    result_expect4 = tree.find_path(node3.id,node5.id)
    result_expect0 = tree.find_path(node7.id,node4.id)
    
    assert len(result_expect0) == 0
    assert len(result_expect4) == 4






    
