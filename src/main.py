from db.database import get_connection, initialize_db

if __name__ == "__main__":
    conn = get_connection()
    initialize_db(conn)
    print("Database schema has been created!")
    conn.close()