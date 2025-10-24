import sqlite3
import os

def reset_payment_tables():
    db_path = os.path.join(os.path.dirname(__file__), 'gym.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # Drop and recreate transactions table
    c.execute('DROP TABLE IF EXISTS transactions')
    c.execute('''
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_type TEXT,
            amount REAL,
            description TEXT,
            created_by INTEGER,
            payment_date TEXT
        )
    ''')
    # Drop and recreate member_payments table
    c.execute('DROP TABLE IF EXISTS member_payments')
    c.execute('''
        CREATE TABLE member_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id TEXT,
            transaction_id INTEGER,
            payment_date TEXT,
            due_date TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("Payment tables reset.")

if __name__ == "__main__":
    reset_payment_tables()
