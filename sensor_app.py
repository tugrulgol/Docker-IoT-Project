import time
import board
import adafruit_dht
import RPi.GPIO as GPIO
import json
from mqtt_handler import publish_data, disconnect_mqtt  # Yeni modülü içe aktar

# GPIO Pin Configurations
DHT_SENSOR1 = adafruit_dht.DHT22(board.D4)  # GPIO 4 #pin_no=7
DHT_SENSOR2 = adafruit_dht.DHT22(board.D17) # GPIO 17 #pin_no=11
BUZZER_PIN = 22  # GPIO 22

# MQTT Topics
MQTT_TOPIC_SENSOR1 = "sensor1/data"
MQTT_TOPIC_SENSOR2 = "sensor2/data"
MQTT_TOPIC_ERROR = "sensor/error"

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

def buzz_on():
    GPIO.output(BUZZER_PIN, GPIO.HIGH)

def buzz_off():
    GPIO.output(BUZZER_PIN, GPIO.LOW)

try:
    while True:
        alert_triggered = False  # Track if an alert is triggered
        try:
            # Reading data from sensor 1
            temperature1 = DHT_SENSOR1.temperature
            humidity1 = DHT_SENSOR1.humidity
            print(f"Sensor 1 - Temp: {temperature1}, Humidity: {humidity1}")
            
            if humidity1 is not None and temperature1 is not None:
                temperature1 = round(temperature1, 4)
                humidity1 = round(humidity1, 4)

                # JSON payload for sensor 1
                sensor1_data = json.dumps({
                    "temperature": temperature1,
                    "humidity": humidity1
                })
                
                # Send combined data to one topic
                publish_data(MQTT_TOPIC_SENSOR1, sensor1_data)
            else:
                # Send alert if data is None
                publish_data(MQTT_TOPIC_ERROR, "Sensor 1 Error")
                print("Sensor 1 Error")
                alert_triggered = True

        except RuntimeError as error:
            # Send alert if there's a RuntimeError
            publish_data(MQTT_TOPIC_ERROR, "Sensor 1 Error")
            print(f"Error reading sensor 1: {error.args[0]}")
            alert_triggered = True
            time.sleep(2.0)  # Wait before retrying

        try:
            # Reading data from sensor 2
            temperature2 = DHT_SENSOR2.temperature
            humidity2 = DHT_SENSOR2.humidity
            print(f"Sensor 2 - Temp: {temperature2}, Humidity: {humidity2}")
            
            if humidity2 is not None and temperature2 is not None:
                temperature2 = round(temperature2, 4)
                humidity2 = round(humidity2, 4)

                # JSON payload for sensor 2
                sensor2_data = json.dumps({
                    "temperature": temperature2,
                    "humidity": humidity2
                })
                
                # Send combined data to one topic
                publish_data(MQTT_TOPIC_SENSOR2, sensor2_data)
            else:
                # Send alert if data is None
                publish_data(MQTT_TOPIC_ERROR, "Sensor 2 Error")
                print("Sensor 2 Error")
                alert_triggered = True

        except RuntimeError as error:
            # Send alert if there's a RuntimeError
            publish_data(MQTT_TOPIC_ERROR, "Sensor 2 Error")
            print(f"Error reading sensor 2: {error.args[0]}")
            alert_triggered = True
            time.sleep(2.0)  # Wait before retrying

        # Check thresholds for either sensor
        if ((humidity1 is not None and temperature1 is not None and (temperature1 > 30 or humidity1 > 70)) or
            (humidity2 is not None and temperature2 is not None and (temperature2 > 30 or humidity2 > 70))):
            publish_data(MQTT_TOPIC_ERROR, "Threshold Exceeded")
            print("Threshold Exceeded")
            alert_triggered = True

        # Trigger the buzzer if any alert is triggered
        if alert_triggered:
            buzz_on()
            time.sleep(2)  # 2 saniye boyunca buzzer açık kalır
            buzz_off()
            time.sleep(1)  # 1 saniye boyunca buzzer kapalı kalır
            buzz_on()
            time.sleep(2)  # 2 saniye boyunca buzzer açık kalır
            buzz_off()
        else:
            buzz_off()

        time.sleep(10)  # Main loop delay

except KeyboardInterrupt:
    GPIO.cleanup()
    disconnect_mqtt()  # MQTT bağlantısını sonlandır
