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
    A[inject\n5초 interval] --> B[function\n쿼리 세팅]
    B --> C[MySQL\nSELECT LIMIT 20]
    C --> D[function\n센서값 분기\n6 outputs]
    D -->|out1| E[gauge\nTemperature]
    D -->|out2| F[gauge\nHumidity]
    D -->|out3| G[gauge\nPressure]
    D -->|out4| H[chart\nTemperature 개별]
    D -->|out5| I[chart\nHumidity 개별]
    D -->|out6| J[chart\nPressure 개별]
```

### 설치 필요 팔레트

Node-RED 메뉴 → **Manage palette** → Install 탭에서 설치:

```
node-red-dashboard
node-red-node-mysql
```

### Flow import 방법

1. Node-RED 우상단 메뉴 → **Import**
2. `nodered-flow.json` 파일 내용 붙여넣기 → **Import** 클릭
3. MySQL 노드 더블클릭 → Database 설정에서 user/password 입력 후 **Update**
4. **Deploy** 클릭

### 노드별 설정 상세

| 노드 | 설정값 |
|------|--------|
| inject | Repeat: interval / every **5** seconds |
| MySQL | Host: `127.0.0.1`, Port: `3306`, Database: `sensordb` |
| gauge × 3 | Min: `0`, Max: `100`, Tab: Sensor Monitor |
| ui_chart | Type: Line, Y-axis 0~100, Remove older: 1시간 |

### 대시보드 접속

```
http://localhost:1880/ui
```

---

## 3. Grafana 대시보드 설명

```mermaid
flowchart LR
    A[Grafana\nData Sources] --> B[MySQL\nlocalhost:3306\nsensordb]
    B --> C[Dashboard Panel\nTime series]
    C --> D["SQL 쿼리\nSELECT created_at AS time,\ntemperature, humidity, pressure\nFROM sensor_data\nORDER BY created_at DESC\nLIMIT 100"]
    D --> E[실시간 그래프\n자동 새로고침 5s]
```

**Grafana 패널 쿼리 (각 패널 개별 적용)**

Temperature:
```sql
SELECT created_at AS time, temperature AS value
FROM sensor_data WHERE created_at >= NOW() - INTERVAL 1 HOUR
ORDER BY created_at ASC
```
Humidity:
```sql
SELECT created_at AS time, humidity AS value
FROM sensor_data WHERE created_at >= NOW() - INTERVAL 1 HOUR
ORDER BY created_at ASC
```
Pressure:
```sql
SELECT created_at AS time, pressure AS value
FROM sensor_data WHERE created_at >= NOW() - INTERVAL 1 HOUR
ORDER BY created_at ASC
```

**Grafana 주요 설정**
- Data Source: MySQL, Host=`localhost:3306`, Database=`sensordb`
- Panel Type: Time series (개별 3패널)
- Format: Time series
- Auto refresh: 5s
- 접속: `http://localhost:3000`
- 참고: `$__timeFilter` 대신 `NOW() - INTERVAL 1 HOUR` 사용 (KST 저장으로 인한 시간대 문제)

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
