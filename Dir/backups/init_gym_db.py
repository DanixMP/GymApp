db_path = r'd:\Pyserver\014 GYM\Gym\Scripts\Dir\gym.db'
import sqlite3
import os
import sys

# If running as a script, execute the database initialization
if __name__ == "__main__":
    db_path = os.path.join(os.path.dirname(__file__), 'gym.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Drop and recreate members table with gender and start_date
    c.execute('DROP TABLE IF EXISTS members')
    c.execute('''
        CREATE TABLE members (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            family TEXT NOT NULL,
            gender TEXT NOT NULL,
            phone TEXT,
            start_date TEXT
        )
    ''')

    # Dummy members with gender and start_date
    import datetime
    today = datetime.date.today().isoformat()
    c.executemany('INSERT INTO members (id, name, family, gender, phone, start_date) VALUES (?, ?, ?, ?, ?, ?)', [
        ("1001", "علی", "رضایی", "men", "09120000001", today),
        ("1002", "مریم", "کاظمی", "women", "09120000002", today),
        ("1003", "حسین", "محمدی", "men", "09120000003", today),
        ("1004", "سارا", "احمدی", "women", "09120000004", today)
    ])

    # Drop and recreate admins table
    c.execute('DROP TABLE IF EXISTS admins')
    c.execute('''
        CREATE TABLE admins (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')

    # Dummy admin
    c.execute('INSERT INTO admins (username, password) VALUES (?, ?)', ("admin", "admin123"))

    conn.commit()
    conn.close()

    print("Database reset. Members and admins added.")
