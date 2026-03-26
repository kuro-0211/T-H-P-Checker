# Project: IoT Sensor Dashboard

랜덤 센서 데이터를 MySQL에 주입하고, Node-RED 및 Grafana 대시보드에서 실시간으로 모니터링하는 통합 IoT 실습 프로젝트입니다.

---

## 시스템 구성

| 컴포넌트 | 역할 |
|----------|------|
| **injector.py** | Python으로 랜덤 센서값(temperature, humidity, pressure) 생성 → MySQL INSERT |
| **MySQL (LAMP)** | 센서 데이터 영구 저장소 |
| **Node-RED** | MySQL에서 데이터를 읽어 웹 대시보드로 실시간 시각화 |
| **Grafana** | MySQL을 데이터소스로 연결, 시계열 그래프 실시간 모니터링 |
| **Mosquitto** | MQTT 브로커 — mqtt-pub.py에서 topic `temp1`으로 publish |

---

## 전체 동작 흐름

```mermaid
flowchart TD
    A([injector.py\n5초마다 실행]) -->|temperature / humidity / pressure| B[(MySQL\nsensordb.sensor_data)]

    B -->|SELECT 주기 조회| C[Node-RED\nMySQL 노드]
    C -->|gauge / chart| D[Node-RED Dashboard\n실시간 웹 UI]

    B -->|데이터소스 연결| E[Grafana\nMySQL DataSource]
    E -->|시계열 패널| F[Grafana Dashboard\n실시간 그래프]

    G([mqtt-pub.py\n5초마다 실행]) -->|topic: temp1| H{{Mosquitto Broker}}
    H -->|subscribe| C
```

---

## 1. injector.py 동작 설명

```mermaid
flowchart LR
    A[시작] --> B[MySQL 연결\nlocalhost:3306/sensordb]
    B --> C{연결 성공?}
    C -- No --> Z[오류 출력 후 종료]
    C -- Yes --> D[루프 시작]
    D --> E[random.uniform 으로\ntemperature/humidity/pressure 생성]
    E --> F[INSERT INTO sensor_data]
    F --> G[commit]
    G --> H[5초 대기]
    H --> D
```

---

## 2. Node-RED 플로우 설명

```mermaid
flowchart LR
    A[inject 노드\n5초 interval] --> B[MySQL 노드\nSELECT 최신 1건]
    B --> C[function 노드\n데이터 파싱]
    C --> D[gauge 노드\ntemperature]
    C --> E[gauge 노드\nhumidity]
    C --> F[gauge 노드\npressure]
    C --> G[chart 노드\n시계열 그래프]
```

**Node-RED 주요 설정**
- MySQL 노드: `localhost`, `sensordb`, user/password 설정
- inject 노드: repeat interval = 5초
- 대시보드 접속: `http://localhost:1880/ui`

---

## 3. Grafana 대시보드 설명

```mermaid
flowchart LR
    A[Grafana\nData Sources] --> B[MySQL\nlocalhost:3306\nsensordb]
    B --> C[Dashboard Panel\nTime series]
    C --> D["SQL 쿼리\nSELECT created_at AS time,\ntemperature, humidity, pressure\nFROM sensor_data\nORDER BY created_at DESC\nLIMIT 100"]
    D --> E[실시간 그래프\n자동 새로고침 5s]
```

**Grafana 주요 설정**
- Data Source: MySQL, Host=`localhost:3306`, Database=`sensordb`
- Panel Type: Time series
- Auto refresh: 5s
- 접속: `http://localhost:3000`

---

## 4. MQTT 흐름

```mermaid
flowchart LR
    A([mqtt-pub.py]) -->|publish\ntopic: temp1\n난수 0~100| B{{Mosquitto\nlocalhost:1883}}
    B -->|subscribe\ntopic: temp1| C[Node-RED\nMQTT in 노드]
    C --> D[Node-RED Dashboard\n실시간 표시]
```

---

## 5. 전체 실행 순서

```mermaid
sequenceDiagram
    participant U as 사용자
    participant I as injector.py
    participant DB as MySQL
    participant NR as Node-RED
    participant GF as Grafana

    U->>I: uv run injector.py
    loop 5초마다
        I->>DB: INSERT sensor_data
        NR->>DB: SELECT 최신값
        DB-->>NR: rows 반환
        NR-->>NR: Dashboard 갱신
        GF->>DB: 쿼리 (auto-refresh)
        DB-->>GF: rows 반환
        GF-->>GF: Panel 갱신
    end
```

---

## MySQL 초기 설정 SQL

```sql
CREATE DATABASE IF NOT EXISTS sensordb;
USE sensordb;
CREATE TABLE IF NOT EXISTS sensor_data (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    temperature FLOAT,
    humidity    FLOAT,
    pressure    FLOAT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
```
