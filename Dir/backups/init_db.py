import sqlite3
import os

def init_gym_db(db_path='gym.db'):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

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

