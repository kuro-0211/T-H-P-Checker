"""
injector.py
-----------
LAMP MySQL에 랜덤 센서 데이터(temperature, humidity, pressure)를
5초 간격으로 INSERT 합니다.
DB/테이블이 없으면 자동으로 생성합니다.
"""

import random
import time
from datetime import datetime, timezone, timedelta
import mysql.connector
from mysql.connector import Error

KST = timezone(timedelta(hours=9))

# ── 설정 ──────────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "chelly",        # MySQL 사용자명
    "password": "jjk00jjk",            # MySQL 비밀번호
    "database": "sensordb",
}
INTERVAL = 5  # 초
# ──────────────────────────────────────────────────────


def setup_db() -> None:
    """DB와 테이블이 없으면 자동 생성"""
    db = DB_CONFIG["database"]

    # 1단계: database 없이 연결 → DB 생성
    init_cfg = {k: v for k, v in DB_CONFIG.items() if k != "database"}
    init_cfg["autocommit"] = True
    conn = mysql.connector.connect(**init_cfg)
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db}` CHARACTER SET utf8mb4")
    cursor.fetchall()
    cursor.close()
    conn.close()

    # 2단계: DB 지정 후 재연결 → 테이블 생성
    cfg = dict(DB_CONFIG)
    cfg["autocommit"] = True
    conn = mysql.connector.connect(**cfg)
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS sensor_data ("
        "id INT AUTO_INCREMENT PRIMARY KEY, "
        "temperature FLOAT, "
        "humidity FLOAT, "
        "pressure FLOAT, "
        "created_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
    )
    cursor.fetchall()
    cursor.close()
    conn.close()
    print(f"DB `{db}` 및 테이블 sensor_data 준비 완료")


def generate_data() -> dict:
    """0~100 사이 난수 센서값 생성"""
    return {
        "temperature": round(random.uniform(0, 100), 2),
        "humidity":    round(random.uniform(0, 100), 2),
        "pressure":    round(random.uniform(0, 100), 2),
    }


def insert(cursor, data: dict) -> None:
    sql = """
        INSERT INTO sensor_data (temperature, humidity, pressure, created_at)
        VALUES (%(temperature)s, %(humidity)s, %(pressure)s, %(created_at)s)
    """
    data["created_at"] = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(sql, data)


def main():
    setup_db()

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
