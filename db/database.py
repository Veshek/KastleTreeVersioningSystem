import sqlite3

def get_connection(db_path="tree_system.db"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db(conn, schema_path="db/schema.sql"):
    with open(schema_path, "r") as f:
        conn.executescript(f.read())