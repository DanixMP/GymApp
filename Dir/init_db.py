import sqlite3
import os

def init_gym_db(db_path='gym.db'):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Create or modify members table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                family TEXT NOT NULL,
                gender TEXT NOT NULL,
                phone TEXT,
                join_date DATE DEFAULT CURRENT_DATE,
                start_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Check if join_date column exists, if not add it
        cursor.execute("PRAGMA table_info(members)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'join_date' not in columns:
            try:
                cursor.execute('ALTER TABLE members ADD COLUMN join_date DATE DEFAULT CURRENT_DATE')
                # Set join_date to created_at for existing members
                cursor.execute('UPDATE members SET join_date = created_at WHERE join_date IS NULL')
                print("Added join_date column to members table")
            except sqlite3.OperationalError as e:
                if 'duplicate column name' not in str(e).lower():
                    raise

        # Create settings table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create transactions table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_type TEXT NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                description TEXT,
                payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS member_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER NOT NULL,
                transaction_id INTEGER NOT NULL,
                payment_date TIMESTAMP NOT NULL,
                due_date TIMESTAMP NOT NULL,
                status TEXT DEFAULT 'paid'
            )
        ''')

        cursor.execute("SELECT value FROM settings WHERE key = 'monthly_fee'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", ('monthly_fee', '500000'))

        conn.commit()
        print("Database checked and updated non-destructively.")

if __name__ == "__main__":
    db_path = os.path.join(os.path.dirname(__file__), 'gym.db')
    init_gym_db(db_path)

