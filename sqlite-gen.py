import sqlite3
import random
import time

DB_PATH = "chellydb"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS sensor (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        humid REAL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()

print("DB 초기화 완료. 10초마다 humid 값을 저장합니다. (종료: Ctrl+C)")

try:
    while True:
        humid = random.randint(0, 100)
        cursor.execute("INSERT INTO sensor (humid) VALUES (?)", (humid,))
        conn.commit()
        print(f"저장됨: humid={humid}")
        time.sleep(10)
except KeyboardInterrupt:
    print("\n종료합니다.")
finally:
    conn.close()
