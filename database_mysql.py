import os
import pymysql

class Database:
    def __init__(self):

        db_port = os.getenv("DB_PORT")
        if not db_port or not db_port.isdigit():
            db_port = "3306"

        self.config = {
            "host": os.getenv("DB_HOST"),
            "port": int(db_port),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASS"),
            "database": os.getenv("DB_NAME"),
            "charset": "utf8mb4",
            "cursorclass": pymysql.cursors.DictCursor,
            "connect_timeout": 10
        }

        print("[DEBUG] DB_HOST =", os.getenv("DB_HOST"))
        print("[DEBUG] DB_PORT =", db_port)
        print("[DEBUG] DB_USER =", os.getenv("DB_USER"))
        print("[DEBUG] DB_NAME =", os.getenv("DB_NAME"))

        self.init_database()

    def get_connection(self):
        return pymysql.connect(**self.config)

    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            telegram_id BIGINT UNIQUE,
            username VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        cursor.close()
        conn.close()

    # Check if user exists
    def user_exists(self, telegram_id):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM users WHERE telegram_id=%s",
            (telegram_id,)
        )

        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return result is not None

    # Add new user
    def add_user(self, telegram_id, username):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT IGNORE INTO users (telegram_id, username) VALUES (%s, %s)",
            (telegram_id, username)
        )

        conn.commit()
        cursor.close()
        conn.close()
