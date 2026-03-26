"""
injector.py
-----------
LAMP MySQL에 랜덤 센서 데이터(temperature, humidity, pressure)를
5초 간격으로 INSERT 합니다.

사전 준비 (MySQL):
    CREATE DATABASE sensordb;
    USE sensordb;
    CREATE TABLE sensor_data (
        id        INT AUTO_INCREMENT PRIMARY KEY,
        temperature FLOAT,
        humidity    FLOAT,
        pressure    FLOAT,
        created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
    );
"""

import random
import time
import mysql.connector
from mysql.connector import Error

# ── 설정 ──────────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",        # MySQL 사용자명
    "password": "",            # MySQL 비밀번호
    "database": "sensordb",
}
INTERVAL = 5  # 초
# ──────────────────────────────────────────────────────


def generate_data() -> dict:
    """0~100 사이 난수 센서값 생성"""
    return {
        "temperature": round(random.uniform(0, 100), 2),
        "humidity":    round(random.uniform(0, 100), 2),
        "pressure":    round(random.uniform(0, 100), 2),
    }


def insert(cursor, data: dict) -> None:
    sql = """
        INSERT INTO sensor_data (temperature, humidity, pressure)
        VALUES (%(temperature)s, %(humidity)s, %(pressure)s)
    """
    cursor.execute(sql, data)


def main():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print(f"MySQL 연결 성공 ({DB_CONFIG['host']}:{DB_CONFIG['port']} / {DB_CONFIG['database']})")
        print(f"{INTERVAL}초마다 랜덤 데이터를 INSERT합니다. (종료: Ctrl+C)\n")

        while True:
            data = generate_data()
            insert(cursor, data)
            conn.commit()
            print(
                f"[INSERT] temperature={data['temperature']:6.2f} | "
                f"humidity={data['humidity']:6.2f} | "
                f"pressure={data['pressure']:6.2f}"
            )
            time.sleep(INTERVAL)

    except Error as e:
        print(f"[MySQL 오류] {e}")
    except KeyboardInterrupt:
        print("\n종료합니다.")
    finally:
        if "cursor" in dir():
            cursor.close()
        if "conn" in dir() and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    main()
