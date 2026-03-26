# sqlite-node-red

SQLite / MySQL + MQTT + Node-RED + Grafana 연동 실습 프로젝트

## 파일 구성

| 파일 | 설명 |
|------|------|
| `sqlite-gen.py` | SQLite(`chellydb`) sensor 테이블에 10초마다 humid 난수 저장 |
| `node-red-gen.py` | SQLite(`chellydb1`) sensor 테이블에 5초마다 humid 난수 저장 |
| `mqtt-pub.py` | MQTT `temp1` 토픽으로 5초마다 난수 publish |
| `injector.py` | MySQL(`sensordb`) sensor_data 테이블에 5초마다 랜덤 센서값 INSERT |

## 환경

- Python 3.12 (uv 가상환경)
- Mosquitto MQTT Broker
- MySQL (LAMP)
- Node-RED
- Grafana

## 실행

```bash
# SQLite 데이터 생성
uv run sqlite-gen.py
uv run node-red-gen.py

# MQTT publish
uv run mqtt-pub.py

# MySQL 데이터 주입
uv run injector.py
```

## MySQL 사전 설정

```sql
CREATE DATABASE sensordb;
USE sensordb;
CREATE TABLE sensor_data (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    temperature FLOAT,
    humidity    FLOAT,
    pressure    FLOAT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

자세한 동작 설명 및 flowchart는 [project.md](./project.md) 참조
