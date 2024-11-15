import paho.mqtt.client as mqtt

# MQTT Configuration
MQTT_BROKER = "mqtt"  # Docker service name for MQTT
MQTT_PORT = 1883  # MQTT port

# MQTT Client Setup
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

def publish_data(topic, message):
    result = client.publish(topic, message)
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print(f"Successfully published to {topic}: {message}")
    else:
        print(f"Failed to publish to {topic}: {message}, Result: {result.rc}")

def disconnect_mqtt():
    client.disconnect()  # Disconnect MQTT client when program ends
