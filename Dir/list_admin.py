import sqlite3


def list_admins_and_remove_others(db_path="Dir/gym.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # List all admins
    cursor.execute("SELECT id, username, full_name, email, created_at FROM users WHERE role='admin' AND is_active=1")
    admins = cursor.fetchall()
    if not admins:
        print("No admins found.")
    else:
        print("Registered Admins before removal:")
        for admin in admins:
            print(f"ID: {admin[0]}, Username: {admin[1]}, Name: {admin[2]}, Email: {admin[3]}, Created: {admin[4]}")
    # Remove all admins except ID 1
    cursor.execute("DELETE FROM users WHERE role='admin' AND id != 1")
    conn.commit()
    # List remaining admins
    cursor.execute("SELECT id, username, full_name, email, created_at FROM users WHERE role='admin' AND is_active=1")
    remaining = cursor.fetchall()
    print("\nAdmins remaining after removal:")
    if not remaining:
        print("No admins remaining.")
    else:
        for admin in remaining:
            print(f"ID: {admin[0]}, Username: {admin[1]}, Name: {admin[2]}, Email: {admin[3]}, Created: {admin[4]}")
    conn.close()

if __name__ == "__main__":
    list_admins_and_remove_others()