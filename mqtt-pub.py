import random
import time
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "temp1"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(BROKER, PORT)
client.loop_start()

print(f"MQTT 브로커({BROKER})에 연결됨. 5초마다 topic '{TOPIC}'으로 publish합니다. (종료: Ctrl+C)")

try:
    while True:
        value = random.randint(0, 100)
        client.publish(TOPIC, value)
        print(f"publish: topic={TOPIC}, value={value}")
        time.sleep(5)
except KeyboardInterrupt:
    print("\n종료합니다.")
finally:
    client.loop_stop()
    client.disconnect()
