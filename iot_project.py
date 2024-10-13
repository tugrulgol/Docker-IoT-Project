import time
import board
import adafruit_dht
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import json
import datetime

# GPIO Pin Configurations
DHT_SENSOR1 = adafruit_dht.DHT22(board.D4)  # GPIO 4 #pin_no=7
DHT_SENSOR2 = adafruit_dht.DHT22(board.D17) # GPIO 17 #pin_no=11
BUZZER_PIN = 22  # GPIO 22

# MQTT Configuration
MQTT_BROKER = "mqtt"  # Docker service name for MQTT
MQTT_PORT = 1883  # MQTT port
MQTT_TOPIC_SENSOR1 = "sensor1/data"
MQTT_TOPIC_SENSOR2 = "sensor2/data"
MQTT_TOPIC_ERROR = "sensor/error"
MQTT_TOPIC_CONTROL_GLOBAL = "sensor/control"  # Global control topic
MQTT_TOPIC_CONTROL_SENSOR1 = "sensor1/control"  # Sensor 1 control topic
MQTT_TOPIC_CONTROL_SENSOR2 = "sensor2/control"  # Sensor 2 control topic

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# MQTT Client Setup
client = mqtt.Client()

# Global variables
collect_data_global = False  # Global data collection control
collect_data_sensor1 = False  # Sensor 1 data collection control
collect_data_sensor2 = False  # Sensor 2 data collection control
last_global_command = None   # Last global command

# MQTT connection and message handling
def on_connect(client, userdata, flags, rc):
    print(f"[{datetime.datetime.now()}] Connected with result code {rc}")
    client.subscribe([(MQTT_TOPIC_CONTROL_GLOBAL, 0), 
                      (MQTT_TOPIC_CONTROL_SENSOR1, 0), 
                      (MQTT_TOPIC_CONTROL_SENSOR2, 0)])  # Subscribe to control topics

def on_message(client, userdata, message):
    global collect_data_global, collect_data_sensor1, collect_data_sensor2, last_global_command
    msg = message.payload.decode('utf-8')
    topic = message.topic
    print(f"[{datetime.datetime.now()}] Received message: {msg} on topic: {topic}")
    
    # Process global control topic
    if topic == MQTT_TOPIC_CONTROL_GLOBAL:
        if msg == last_global_command:
            print(f"[{datetime.datetime.now()}] Global command already processed, skipping: {msg}")
            return

        if msg == 'start':
            collect_data_global = True
            print(f"[{datetime.datetime.now()}] Global data collection started")
        elif msg == 'stop':
            collect_data_global = False
            print(f"[{datetime.datetime.now()}] Global data collection stopped")

        last_global_command = msg  # Save the last processed global command

    # Process individual sensor control topics
    elif topic == MQTT_TOPIC_CONTROL_SENSOR1:
        collect_data_sensor1 = (msg == 'start')
        print(f"[{datetime.datetime.now()}] Sensor 1 data collection {'started' if collect_data_sensor1 else 'stopped'}")

    elif topic == MQTT_TOPIC_CONTROL_SENSOR2:
        collect_data_sensor2 = (msg == 'start')
        print(f"[{datetime.datetime.now()}] Sensor 2 data collection {'started' if collect_data_sensor2 else 'stopped'}")

# Setup MQTT callbacks
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Start MQTT loop
client.loop_start()

def publish_data(topic, message):
    result = client.publish(topic, message)
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print(f"Successfully published to {topic}: {message}")
    else:
        print(f"Failed to publish to {topic}: {message}, Result: {result.rc}")

def buzz_on():
    GPIO.output(BUZZER_PIN, GPIO.HIGH)

def buzz_off():
    GPIO.output(BUZZER_PIN, GPIO.LOW)

try:
    while True:
        alert_triggered = False  # Track if an alert is triggered
        
        # Only collect data if global control is True
        if collect_data_global:
            # Sensor 1 data collection
            if collect_data_sensor1:
                try:
                    temperature1 = DHT_SENSOR1.temperature
                    humidity1 = DHT_SENSOR1.humidity
                    print(f"Sensor 1 - Temp: {temperature1}, Humidity: {humidity1}")
                    
                    if humidity1 is not None and temperature1 is not None:
                        sensor1_data = json.dumps({
                            "temperature": round(temperature1, 4),
                            "humidity": round(humidity1, 4)
                        })
                        publish_data(MQTT_TOPIC_SENSOR1, sensor1_data)
                    else:
                        publish_data(MQTT_TOPIC_ERROR, "Sensor 1 Error")
                        alert_triggered = True

                except RuntimeError as error:
                    publish_data(MQTT_TOPIC_ERROR, "Sensor 1 Error")
                    alert_triggered = True
                    time.sleep(2.0)

            # Sensor 2 data collection
            if collect_data_sensor2:
                try:
                    temperature2 = DHT_SENSOR2.temperature
                    humidity2 = DHT_SENSOR2.humidity
                    print(f"Sensor 2 - Temp: {temperature2}, Humidity: {humidity2}")
                    
                    if humidity2 is not None and temperature2 is not None:
                        sensor2_data = json.dumps({
                            "temperature": round(temperature2, 4),
                            "humidity": round(humidity2, 4)
                        })
                        publish_data(MQTT_TOPIC_SENSOR2, sensor2_data)
                    else:
                        publish_data(MQTT_TOPIC_ERROR, "Sensor 2 Error")
                        alert_triggered = True

                except RuntimeError as error:
                    publish_data(MQTT_TOPIC_ERROR, "Sensor 2 Error")
                    alert_triggered = True
                    time.sleep(2.0)

            # Trigger the buzzer if any alert is triggered
            if alert_triggered:
                buzz_on()
            else:
                buzz_off()
        else:
            print(f"[{datetime.datetime.now()}] Global data collection is stopped.")

        time.sleep(10)

except KeyboardInterrupt:
    GPIO.cleanup()
    client.disconnect()
