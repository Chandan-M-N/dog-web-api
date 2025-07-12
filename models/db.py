# models/db.py
import psycopg2
from typing import List, Dict, Optional

DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "dogwebapi",
    "host": "localhost",
    "port": "5432"
}

def get_db_connection():
    """Establish and return a database connection"""
    return psycopg2.connect(**DB_CONFIG)

def get_all_dogs() -> List[Dict[str, Optional[str]]]:
    """
    Fetch all dogs from database
    Returns: List of dictionaries with breed and sub_breed
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT id, breed, sub_breed 
            FROM dogs 
            ORDER BY breed, sub_breed
        """)
        
        dogs = []
        for row in cur.fetchall():
            dogs.append({
                "id": row[0],
                "breed": row[1],
                "sub_breed": row[2]
            })
            
        return dogs
        
    except Exception as e:
        print(f"Database error: {e}")
        raise 
    finally:
        cur.close()
        conn.close()