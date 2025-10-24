import sqlite3
import os

def migrate_add_end_date():
    db_path = os.path.join(os.path.dirname(__file__), 'gym.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Check if end_date column exists
    cursor.execute("PRAGMA table_info(members)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'end_date' not in columns:
        cursor.execute("ALTER TABLE members ADD COLUMN end_date TEXT")
        print("Added end_date column to members table.")
    else:
        print("end_date column already exists.")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate_add_end_date()
