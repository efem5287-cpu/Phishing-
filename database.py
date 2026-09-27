import sqlite3

DB_NAME = "bot_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            referred_by INTEGER,
            is_active INTEGER DEFAULT 0,
            referral_count INTEGER DEFAULT 0,
            unlocked INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def add_user(user_id, referred_by=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    if not row:
        cursor.execute("INSERT INTO users (user_id, referred_by) VALUES (?, ?)", (user_id, referred_by))
        if referred_by and referred_by != user_id:
            # Check if referrer exists
            cursor.execute("SELECT referral_count FROM users WHERE user_id = ?", (referred_by,))
            ref_row = cursor.fetchone()
            if ref_row:
                new_count = ref_row[0] + 1
                cursor.execute("UPDATE users SET referral_count = ? WHERE user_id = ?", (new_count, referred_by))
                cursor.execute("SELECT unlocked FROM users WHERE user_id = ?", (referred_by,))
                unlocked_status = cursor.fetchone()[0]
                if new_count >= 2 and not unlocked_status:
                    cursor.execute("UPDATE users SET unlocked = 1 WHERE user_id = ?", (referred_by,))
        conn.commit()
    conn.close()

def mark_active(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_active = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_user_stats(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT referral_count, unlocked FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0], row[1]
    return 0, 0
      
