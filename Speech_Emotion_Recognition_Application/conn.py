import sqlite3

def create_database():
    conn = sqlite3.connect('emotionrecognizer.db')
    cursor = conn.cursor()

    # Create the endusers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS endusers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    ''')

    # Create the records table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        file_path TEXT NOT NULL,
        cloud_link TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES endusers (id)
    )
    ''')

    conn.commit()
    cursor.close()
    conn.close()
    print("Database and tables created successfully!")

create_database()

import sqlite3
import time
from Upload import *

def get_db_connection():
    return sqlite3.connect('emotionrecognizer.db')

def check_user(username, password):
    """Check if the username and password match in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # SQL query to check if the username and password match
        query = "SELECT * FROM endusers WHERE username = ? AND password = ?"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()  # Fetch the first result

        if user:
            return True  # User found
        else:
            return False  # User not found
    except sqlite3.Error as err:
        print(f"Error: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def save_record(user_id, file_path):
    """
    Saves the recording details to the database with a cloud link and timestamp.
    """
    cloud_link = upload_file_to_cloudinary(file_path)

    if not cloud_link:
        print("Failed to upload recording to cloud storage.")
        return False

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Use the current time for `recorded_at`
        recorded_at = time.strftime("%Y-%m-%d %H:%M:%S")  # Format: YYYY-MM-DD HH:MM:SS
        query = "INSERT INTO records (user_id, file_path, cloud_link, timestamp) VALUES (?, ?, ?, ?)"
        cursor.execute(query, (user_id, file_path, cloud_link, recorded_at))
        conn.commit()
        print(f"Recording saved successfully with timestamp: {recorded_at}")
        return True
    except sqlite3.Error as err:
        print(f"Database error: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def add_user(username, password):
    """Add a new user to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if the username already exists
        check_query = "SELECT id FROM endusers WHERE username = ?"
        cursor.execute(check_query, (username,))
        if cursor.fetchone():
            return False  # Username already exists

        # Insert the new user into the database
        insert_query = "INSERT INTO endusers (username, password) VALUES (?, ?)"
        cursor.execute(insert_query, (username, password))
        conn.commit()
        return True  # User added successfully
    except sqlite3.Error as err:
        print(f"Error adding user: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def authenticate_user(username, password):
    """Authenticate the user and return their user_id if successful."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Query to check if the username and password match
        query = "SELECT id FROM endusers WHERE username = ? AND password = ?"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()  # Fetch the first matching row

        if result:
            return result[0]  # Return the user id
        else:
            return None  # No matching user found
    except sqlite3.Error as err:
        print(f"Error authenticating user: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_user_records(user_id):
    """
    Fetches all records of a specific user from the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = "SELECT id, cloud_link, file_path, timestamp FROM records WHERE user_id = ? ORDER BY timestamp DESC"
        cursor.execute(query, (user_id,))
        return cursor.fetchall()  # Return a list of records
    except sqlite3.Error as err:
        print(f"Database error: {err}")
        return []
    finally:
        cursor.close()
        conn.close()
