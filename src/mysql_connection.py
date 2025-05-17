import mysql.connector
from datetime import datetime

from src.config import MYSQL_CONFIG

def init_database():
    try:
        print("mysqlconfig: ", MYSQL_CONFIG)
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        print("conn: ", conn)
        cursor = conn.cursor()
        print("cursor: ", cursor)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_input TEXT NOT NULL,
                model_response TEXT,
                timestamp DATETIME NOT NULL
            )
        ''')
        conn.commit()
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
    finally:
        cursor.close()
        conn.close()