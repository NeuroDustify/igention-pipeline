# publisher.py
import paho.mqtt.client as mqtt
import time

# Settings
broker = "test.mosquitto.org"  # Public broker for testing
port = 1883
topic = "test/topic"

# Create a client instance
client = mqtt.Client()

# Connect to broker
client.connect(broker, port, 60)

# Publish a message
while True:
    message = "Hello from publisher!"
    client.publish(topic, message)
    print(f"Published: {message}")
    time.sleep(2)  # Publish every 2 seconds