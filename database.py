import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="vault.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt BLOB NOT NULL
                )
            ''')
            # Entries table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    site_name TEXT NOT NULL,
                    username TEXT NOT NULL,
                    encrypted_password TEXT NOT NULL,
                    url TEXT,
                    category TEXT DEFAULT 'General',
                    is_favorite INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            conn.commit()

    # User operations
    def create_user(self, username, password_hash, salt):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                    (username, password_hash, salt)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def get_user(self, username):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            return cursor.fetchone()

    # Entry operations
    def add_entry(self, user_id, site_name, username, encrypted_password, url, category):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO entries (user_id, site_name, username, encrypted_password, url, category)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, site_name, username, encrypted_password, url, category))
            conn.commit()
            return cursor.lastrowid

    def get_entries(self, user_id, category=None, search_query=None):
        query = "SELECT * FROM entries WHERE user_id = ?"
        params = [user_id]
        
        if category and category != "All":
            query += " AND category = ?"
            params.append(category)
        
        if search_query:
            query += " AND (site_name LIKE ? OR username LIKE ?)"
            params.extend([f"%{search_query}%", f"%{search_query}%"])
            
        query += " ORDER BY site_name ASC"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def update_entry(self, entry_id, site_name, username, encrypted_password, url, category):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE entries 
                SET site_name = ?, username = ?, encrypted_password = ?, url = ?, category = ?
                WHERE id = ?
            ''', (site_name, username, encrypted_password, url, category, entry_id))
            conn.commit()

    def delete_entry(self, entry_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
            conn.commit()
            
    def get_categories(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT category FROM entries WHERE user_id = ?", (user_id,))
            return [row[0] for row in cursor.fetchall()]
