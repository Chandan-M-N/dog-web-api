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

def add_dog(breed: str, sub_breed: Optional[str] = None) -> bool:
    """
    Add a new dog breed or sub-breed to the database
    Returns: True if successful, False if:
        - breed/sub-breed combo already exists
        - breed already exists (when sub_breed is None)
    Special case: If breed exists with NULL sub_breed and we're adding a sub_breed,
                 update the existing record instead of creating a new one
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # First check if we're adding a main breed (sub_breed is None)
        if sub_breed is None:
            cur.execute("""
                SELECT 1 FROM dogs 
                WHERE breed = %s AND sub_breed IS NULL
                LIMIT 1
            """, (breed,))
            if cur.fetchone():
                return False  # Main breed already exists
        
        # Then check if breed/sub-breed combo exists
        cur.execute("""
            SELECT 1 FROM dogs 
            WHERE breed = %s AND sub_breed IS NOT DISTINCT FROM %s
            LIMIT 1
        """, (breed, sub_breed))
        if cur.fetchone():
            return False  # Combo already exists
        
        # Special case: If breed exists with NULL sub_breed and we're adding a sub_breed
        if sub_breed is not None:
            cur.execute("""
                SELECT 1 FROM dogs 
                WHERE breed = %s AND sub_breed IS NULL
                LIMIT 1
            """, (breed,))
            if cur.fetchone():
                # Update existing NULL sub_breed record
                cur.execute("""
                    UPDATE dogs 
                    SET sub_breed = %s
                    WHERE breed = %s AND sub_breed IS NULL
                """, (sub_breed, breed))
                conn.commit()
                return True
        
        # Normal case: Insert new entry
        cur.execute("""
            INSERT INTO dogs (breed, sub_breed)
            VALUES (%s, %s)
        """, (breed, sub_breed))
        
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"Error adding dog: {e}")
        raise
    finally:
        cur.close()
        conn.close()

def add_sub_breed(breed: str, sub_breed: str) -> bool:
    """
    Add a sub-breed to an existing breed
    Handles both cases (empty or existing sub-breeds)
    Returns: True if successful, False if combo exists
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Check if breed exists
        cur.execute("""
            SELECT 1 FROM dogs 
            WHERE breed = %s AND sub_breed IS NULL
            LIMIT 1
        """, (breed,))
        
        if cur.fetchone():
            # Case 1: Breed exists with no sub-breeds
            cur.execute("""
                UPDATE dogs SET sub_breed = %s
                WHERE breed = %s AND sub_breed IS NULL
            """, (sub_breed, breed))
        else:
            # Case 2: Need to add new entry
            return add_dog(breed, sub_breed)
            
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"Error adding sub-breed: {e}")
        raise
    finally:
        cur.close()
        conn.close()

def delete_dog(breed: str, sub_breed: Optional[str] = None) -> bool:
    """
    Delete a breed or specific sub-breed with special handling:
    - If sub_breed is None: deletes ALL entries for the breed
    - If sub_breed is provided:
      - If it's the only entry: sets sub_breed to NULL (keeps breed)
      - If multiple entries exist: deletes just this combo
    Returns: True if any records were modified, False if nothing was found
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        if sub_breed is None:
            # Case 1: Delete entire breed (all sub-breeds)
            cur.execute("""
                DELETE FROM dogs 
                WHERE breed = %s
                RETURNING 1
            """, (breed,))
        else:
            # Case 2: Handle sub-breed deletion
            # First check if this is the only entry for this breed
            cur.execute("""
                SELECT COUNT(*) FROM dogs 
                WHERE breed = %s
            """, (breed,))
            count = cur.fetchone()[0]
            
            if count == 1:
                # Only entry - set sub_breed to NULL
                cur.execute("""
                    UPDATE dogs 
                    SET sub_breed = NULL
                    WHERE breed = %s AND sub_breed = %s
                    RETURNING 1
                """, (breed, sub_breed))
            else:
                # Multiple entries - delete this specific combo
                cur.execute("""
                    DELETE FROM dogs 
                    WHERE breed = %s AND sub_breed = %s
                    RETURNING 1
                """, (breed, sub_breed))
        
        modified = bool(cur.fetchone())
        conn.commit()
        return modified
        
    except Exception as e:
        conn.rollback()
        print(f"Error deleting dog: {e}")
        raise
    finally:
        cur.close()
        conn.close()

def edit_dog(original_breed: str, new_breed: str, 
             original_sub_breed: Optional[str] = None,
             new_sub_breed: Optional[str] = None) -> bool:
    """
    Edit a breed or sub-breed with special handling:
    - If sub_breeds are None: updates ALL entries for the breed
    - If sub_breeds are provided: updates only the specific combo
    Returns: True if updated, False if new combo exists
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Check if new combo already exists (only if we're changing to something new)
        if new_breed != original_breed or new_sub_breed != original_sub_breed:
            cur.execute("""
                SELECT 1 FROM dogs 
                WHERE breed = %s AND sub_breed IS NOT DISTINCT FROM %s
                AND NOT (breed = %s AND sub_breed IS NOT DISTINCT FROM %s)
                LIMIT 1
            """, (new_breed, new_sub_breed, original_breed, original_sub_breed))
            
            if cur.fetchone():
                return False  # New combo exists
        
        # Update the record(s)
        if original_sub_breed is None:
            # Case 1: Update all entries for this breed (main breed and all sub-breeds)
            cur.execute("""
                UPDATE dogs 
                SET breed = %s
                WHERE breed = %s
            """, (new_breed, original_breed))
        else:
            # Case 2: Update specific breed/sub-breed combo
            cur.execute("""
                UPDATE dogs 
                SET breed = %s, sub_breed = %s
                WHERE breed = %s AND sub_breed IS NOT DISTINCT FROM %s
            """, (new_breed, new_sub_breed, original_breed, original_sub_breed))
        
        conn.commit()
        return cur.rowcount > 0
        
    except Exception as e:
        conn.rollback()
        print(f"Error editing dog: {e}")
    finally:
        cur.close()
        conn.close()