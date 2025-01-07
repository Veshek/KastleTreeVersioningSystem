import pytest
import os
from db.database import get_connection, initialize_db
from src.models import Tree

@pytest.fixture
def db_conn():
    conn = get_connection()
    initialize_db(conn)
    yield conn
    conn.close()

def test_tree_creation(db_conn):
    Tree.create('My Configuration')
    tree = Tree.get(tree_id=1)
    new_tag = tree.create_tag("release-v1.0", description="Initial stable release")
    # Making changes to the configuration
    modified_tree =  tree.create_new_tree_version_from_tag("release-v1.0")
    new_node = modified_tree.add_node(data={"setting": "new_value"})
    modified_tree.create_tag("release-v1.1", description="Added new setting")
    # Adding an edge between nodes
    modified_tree.add_edge(node_id_1=1, node_id_2=2, data={"weight": 0.5})
    
    l = input("s")
    





    
