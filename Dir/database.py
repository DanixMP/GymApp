import sqlite3
import bcrypt
from datetime import datetime
from pathlib import Path
import os
import sys
import shutil
from .date_utils import gregorian_to_jalali, jalali_to_gregorian, get_current_jalali_date, format_jalali_date


def _get_writable_app_dir() -> Path:
    """Return a writable per-user application data directory."""
    # Prefer %APPDATA% on Windows; fall back to home directory
    appdata = os.getenv('APPDATA') or os.getenv('LOCALAPPDATA')
    base_dir = Path(appdata) if appdata else (Path.home() / '.gym_app')
    app_dir = base_dir / 'Gym'
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def _resolve_default_db_path() -> str:
    """Resolve a persistent DB path and copy a seed DB on first run if available."""
    user_db_path = _get_writable_app_dir() / 'gym.db'

    if not user_db_path.exists():
        # Try to locate a seed database bundled with the app
        candidates = [
            Path(__file__).parent / 'gym.db',
        ]
        # If running under PyInstaller (onefile), also check the extraction dir
        meipass = getattr(sys, '_MEIPASS', None)
        if meipass:
            candidates.append(Path(meipass) / 'Dir' / 'gym.db')
            candidates.append(Path(meipass) / 'gym.db')
        for candidate in candidates:
            if candidate.exists():
                try:
                    shutil.copy2(str(candidate), str(user_db_path))
                except Exception:
                    # If copy fails, we will initialize an empty DB later
                    pass
                break
    return str(user_db_path)


class Database:
    def get_expiring_members(self, days=7):
        """Return members with less than 'days' days remaining. Returns list of dicts with id and name."""
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, family, end_date, CAST(julianday(end_date) - julianday('now') AS INT) AS remaining_days
                FROM members
                WHERE end_date IS NOT NULL AND CAST(julianday(end_date) - julianday('now') AS INT) < ? AND CAST(julianday(end_date) - julianday('now') AS INT) >= 0
                ORDER BY end_date ASC
            ''', (days,))
            return [dict(row) for row in cursor.fetchall()]

    def get_monthly_fee(self):
        """Get the current monthly fee from settings table."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = 'monthly_fee'")
            row = cursor.fetchone()
            return int(row[0]) if row and row[0] and str(row[0]).isdigit() else 0

    def set_monthly_fee(self, fee):
        """Set the monthly fee in settings table."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE settings SET value = ?, updated_at = CURRENT_TIMESTAMP WHERE key = 'monthly_fee'", (str(fee),))
            if cursor.rowcount == 0:
                cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", ('monthly_fee', str(fee)))
            conn.commit()
    def get_recently_joined_members(self):
        """Return all members who joined in the last 7 days."""
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT *, CASE WHEN end_date IS NOT NULL THEN CAST(julianday(end_date) - julianday('now') AS INT) ELSE NULL END AS remaining_days
                FROM members
                WHERE julianday('now') - julianday(start_date) <= 7
                ORDER BY end_date DESC
            ''')
            return cursor.fetchall()
    def get_members(self, filter_text=None):
        """Return all members, optionally filtered by name, family, phone, or id. Adds remaining_days field."""
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            base_query = '''
                SELECT 
                    *,
                    CASE 
                        WHEN end_date IS NOT NULL THEN CAST(julianday(end_date) - julianday('now') AS INT)
                        ELSE NULL
                    END AS remaining_days,
                    COALESCE(join_date, created_at) as join_date
                FROM members
            '''
            if filter_text:
                cursor.execute(f"{base_query} WHERE name LIKE ? OR family LIKE ? OR phone LIKE ? OR id LIKE ?",
                             [f"%{filter_text}%"]*4)
            else:
                cursor.execute(base_query)
            return cursor.fetchall()

    def add_member(self, id_, name, family, gender, phone, join_date=None, end_date=None):
        """Add a new member with start_date, end_date, and specified join_date."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if join_date and end_date:
                cursor.execute('''
                    INSERT INTO members (id, name, family, gender, phone, start_date, end_date, join_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (id_, name, family, gender, phone, join_date, end_date, join_date))
            elif join_date:
                # Default to 30 days
                from datetime import datetime, timedelta
                end_date_calc = (datetime.strptime(join_date, "%Y-%m-%d") + timedelta(days=30)).strftime("%Y-%m-%d")
                cursor.execute('''
                    INSERT INTO members (id, name, family, gender, phone, start_date, end_date, join_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (id_, name, family, gender, phone, join_date, end_date_calc, join_date))
            else:
                from datetime import datetime, timedelta
                today = datetime.now().strftime("%Y-%m-%d")
                end_date_calc = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
                cursor.execute('''
                    INSERT INTO members (id, name, family, gender, phone, start_date, end_date, join_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (id_, name, family, gender, phone, today, end_date_calc, today))
            conn.commit()
    def update_member(self, member_id, name, family, phone):
        """Update member information."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE members
                SET name = ?, family = ?, phone = ?
                WHERE id = ?
            ''', (name, family, phone, member_id))
            conn.commit()
    def delete_member(self, member_id):
        """Delete a member by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM members WHERE id = ?", (member_id,))
            conn.commit()
    def renew_member_start_date(self, member_id):
        """Renew a member's start_date by adding 30 days to the later of today or current start_date."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT start_date FROM members WHERE id = ?", (member_id,))
            start_date = cursor.fetchone()
            if start_date and start_date[0]:
                cursor.execute('''
                    UPDATE members SET start_date = 
                        CASE 
                            WHEN julianday(start_date) > julianday('now') THEN date(julianday(start_date), '+30 days')
                            ELSE date('now', '+30 days')
                        END
                    WHERE id = ?
                ''', (member_id,))
            else:
                cursor.execute("UPDATE members SET start_date = date('now', '+30 days') WHERE id = ?", (member_id,))
            conn.commit()
    def add_transaction(self, transaction_type, amount, description, created_by):
        """Add a new transaction and return its ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions (transaction_type, amount, description, created_by)
                VALUES (?, ?, ?, ?)
            ''', (transaction_type, amount, description, created_by))
            conn.commit()
            return cursor.lastrowid

    def add_member_payment(self, member_id, transaction_id, payment_date, due_date, status='paid'):
        """Add a new member payment record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO member_payments (member_id, transaction_id, payment_date, due_date, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (member_id, transaction_id, payment_date, due_date, status))
            conn.commit()
            return cursor.lastrowid

    def get_member_payments(self, member_id):
        """Return all payment records for a member, ordered by payment_date descending."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT mp.*, t.amount, t.description, t.transaction_type
                FROM member_payments mp
                JOIN transactions t ON mp.transaction_id = t.id
                WHERE mp.member_id = ?
                ORDER BY mp.payment_date DESC
            ''', (member_id,))
            return cursor.fetchall()

    def get_payments_between_dates(self, start_date, end_date):
        """Return all payments in a date range (for reporting)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT mp.*, t.amount, t.description, t.transaction_type, m.full_name, m.id as member_id
                FROM member_payments mp
                JOIN transactions t ON mp.transaction_id = t.id
                JOIN members m ON mp.member_id = m.id
                WHERE mp.payment_date BETWEEN ? AND ?
                ORDER BY mp.payment_date DESC
            ''', (start_date, end_date))
            return cursor.fetchall()

    def get_last_payment_for_member(self, member_id):
        """Return the most recent payment for a member."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT mp.*, t.amount, t.description, t.transaction_type
                FROM member_payments mp
                JOIN transactions t ON mp.transaction_id = t.id
                WHERE mp.member_id = ?
                ORDER BY mp.payment_date DESC
                LIMIT 1
            ''', (member_id,))
            return cursor.fetchone()
    def get_total_members(self):
        """Return the total number of members."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM members")
            result = cursor.fetchone()
            return result[0] if result else 0

    def get_dashboard_stats(self, current_shift):
        """Return dashboard statistics: total_active, shift_count, expiring, recent."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Total members
            cursor.execute("SELECT COUNT(*) FROM members")
            total_active = cursor.fetchone()
            total_active = total_active[0] if total_active else 0
            # Current shift members
            cursor.execute("SELECT COUNT(*) FROM members WHERE gender=?", (current_shift,))
            shift_count = cursor.fetchone()
            shift_count = shift_count[0] if shift_count else 0
            # Expiring memberships (less than 5 days left)
            cursor.execute("SELECT COUNT(*) FROM members WHERE julianday('now') - julianday(start_date) >= 25 AND julianday('now') - julianday(start_date) < 30")
            expiring = cursor.fetchone()
            expiring = expiring[0] if expiring else 0
            # Recently joined (last 7 days)
            cursor.execute("SELECT COUNT(*) FROM members WHERE julianday('now') - julianday(start_date) <= 7")
            recent = cursor.fetchone()
            recent = recent[0] if recent else 0
            return {
                'total_active': total_active,
                'shift_count': shift_count,
                'expiring': expiring,
                'recent': recent
            }
    def __init__(self, db_path=None):
        if db_path is None:
            # Use a per-user writable location; copy seed DB on first run
            db_path = _resolve_default_db_path()
        self.db_path = db_path
        self.init_database()
        self._migrate_database()  # Add migration step

    def get_connection(self):
        """Create and return a database connection."""
        return sqlite3.connect(self.db_path)
        
    def _migrate_database(self):
        """Handle database migrations."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Check columns in members table
            cursor.execute("PRAGMA table_info(members)")
            columns = [column[1] for column in cursor.fetchall()]
            # Add created_at column if missing
            if 'created_at' not in columns:
                try:
                    cursor.execute("ALTER TABLE members ADD COLUMN created_at TIMESTAMP")
                    # Set created_at to now for existing rows
                    cursor.execute("UPDATE members SET created_at = date('now') WHERE created_at IS NULL")
                    conn.commit()
                    print("Added created_at column to members table")
                except sqlite3.OperationalError as e:
                    if 'duplicate column name' not in str(e).lower():
                        print(f"Migration error: {e}")
                        raise
            # Add join_date column if missing
            if 'join_date' not in columns:
                try:
                    cursor.execute('ALTER TABLE members ADD COLUMN join_date DATE')
                    # Update join_date using created_at if available, else today
                    cursor.execute('''
                        UPDATE members 
                        SET join_date = COALESCE(created_at, date('now'))
                        WHERE join_date IS NULL
                    ''')
                    conn.commit()
                    print("Added join_date column to members table")
                except sqlite3.OperationalError as e:
                    if 'duplicate column name' not in str(e).lower():
                        print(f"Migration error: {e}")
                        raise

    def init_database(self):
        """Initialize the database with required tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Members table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS members (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    family TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    phone TEXT,
                    join_date DATE,
                    start_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    email TEXT UNIQUE,
                    role TEXT NOT NULL DEFAULT 'staff',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Settings table for system-wide configurations
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Transactions table for all financial records
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_type TEXT NOT NULL,  -- 'membership', 'income', 'expense'
                    amount DECIMAL(10, 2) NOT NULL,
                    description TEXT,
                    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER,
                    FOREIGN KEY (created_by) REFERENCES users(id)
                )
            ''')
            
            # Member payments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS member_payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id INTEGER NOT NULL,
                    transaction_id INTEGER NOT NULL,
                    payment_date TIMESTAMP NOT NULL,
                    due_date TIMESTAMP NOT NULL,
                    status TEXT DEFAULT 'paid',  -- 'paid', 'pending', 'overdue'
                    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
                    FOREIGN KEY (member_id) REFERENCES members(id)
                )
            ''')
            
            # Insert default admin user if no users exist
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                self.create_user(
                    username="admin",
                    password="admin123",  # Change this in production!
                    full_name="System Administrator",
                    email="admin@gym.com",
                    role="admin"
                )
            
            # Set default monthly fee if not set
            cursor.execute("SELECT value FROM settings WHERE key = 'monthly_fee'")
            if not cursor.fetchone():
                cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", 
                             ('monthly_fee', '500000'))  # Default 500,000 Tomans

    def create_user(self, username, password, full_name, email, role="staff"):
        """Create a new user with hashed password."""
        password_hash = self._hash_password(password)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO users (username, password_hash, full_name, email, role, is_active)
                    VALUES (?, ?, ?, ?, ?, 1)
                ''', (username, password_hash, full_name, email, role))
                return True
            except sqlite3.IntegrityError:
                return False  # Username or email already exists

    def verify_user(self, username, password):
        """Verify user credentials."""
        # Block dummy user 'aa' from logging in
        if username.strip().lower() == 'aa':
            return None
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, password_hash, role, full_name 
                FROM users 
                WHERE username = ? AND is_active = 1
            ''', (username,))
            user = cursor.fetchone()
            if user and self._check_password(password, user[2]):
                return {
                    'id': user[0],
                    'username': user[1],
                    'role': user[3],
                    'full_name': user[4]
                }
            return None

    def _hash_password(self, password):
        """Hash a password for storing."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)

    def _check_password(self, password, hashed_password):
        """Check if the provided password matches the stored hash."""
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

# Create a global database instance
db = Database()