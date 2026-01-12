import os
import pymysql

class Database:
    def __init__(self):
        self.config = {
            "host": os.getenv("DB_HOST"),
            "port": int(os.getenv("DB_PORT", 3306)),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASS"),
            "database": os.getenv("DB_NAME"),
            "charset": "utf8mb4",
            "cursorclass": pymysql.cursors.DictCursor,
            "connect_timeout": 10
        }

        print(f"[INFO] MySQL Host: {self.config['host']}:{self.config['port']}")
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
