# mqtt_subscriber/subscribe_data.py
# Script to subscribe to MQTT topics and process received data.

import paho.mqtt.client as mqtt
import json
import os
import sys

# --- MQTT Configuration ---
MQTT_BROKER_ADDRESS = "test.mosquitto.org"
MQTT_PORT = 1883
TOPIC_BASE = "suburb/model/igention/"
# Subscribe to all subtopics of TOPIC_BASE
MQTT_TOPIC = TOPIC_BASE + "#"  # '#' is a wildcard in MQTT

# --- MQTT Callbacks ---
def on_connect(client, userdata, flags, rc):
    """Callback function for when the client connects to the MQTT broker."""
    if rc == 0:
        print("Subscriber connected to MQTT broker.")
        client.subscribe(MQTT_TOPIC)  # Subscribe to the topic
    else:
        print(f"Subscriber connection failed with code {rc}")


def on_message(client, userdata, msg):
    """Callback function for when a message is received from the MQTT broker."""

    try:
        payload = json.loads(msg.payload.decode())
        print(f"Received data on topic: {msg.topic}")
        print(json.dumps(payload, indent=2))  # Pretty-print the JSON
    except json.JSONDecodeError:
        print(f"Received non-JSON message on topic: {msg.topic} - {msg.payload.decode()}")
    except Exception as e:
        print(f"Error processing message: {e}")


def on_subscribe(client, userdata, mid, granted_qos):
    """Callback for when the client receives a SUBACK response from the broker."""
    print(f"Subscribed to {MQTT_TOPIC} with QoS: {granted_qos}")


def on_disconnect(client, userdata, rc):
    """Callback function for disconnection."""

    print(f"Disconnected from MQTT broker with code: {rc}")


def main():
    """Main function to connect to MQTT, subscribe, and handle messages."""

    client = mqtt.Client()

    # Set up callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.on_disconnect = on_disconnect

    # Connect to the MQTT broker
    print(f"Connecting to MQTT broker: {MQTT_BROKER_ADDRESS}:{MQTT_PORT}")
    client.connect(MQTT_BROKER_ADDRESS, MQTT_PORT, 60)

    # The loop_forever() method is a blocking loop that handles
    # all network operations and callbacks.  It will run until
    # the client calls disconnect().
    client.loop_forever()


if __name__ == "__main__":
    main()