from db.database import get_connection, initialize_db
from src.Tree import Tree

if __name__ == "__main__":
    conn = get_connection()
    initialize_db(conn)
    print("Database schema has been created!")
    conn.close()

    tree0 = Tree.create('Tree0')
    node_data = {'metadata':1,'data':2}
    node1 = tree0.add_node(node_data)
    node2 = tree0.add_node(node_data)

    tag1 = tree0.create_tag('ver0','simple tree')

    tree0.add_edge(node1.id, node2.id, {'metadata':1,'data':2})

    tree1 = tree0.create_new_tree_version_from_tag(tag1.tag_name)

    

    
    

