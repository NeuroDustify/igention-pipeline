# mqtt_publisher/publish_bin_data.py
# Script to read generated bin data from JSON and publish to MQTT in parallel.

import paho.mqtt.client as mqtt
import json
import os
import time
import concurrent.futures


# --- MQTT Configuration ---
MQTT_BROKER_ADDRESS = "test.mosquitto.org"
MQTT_PORT = 1883
TOPIC_BASE = "suburb/model/igention/"  # Consistent base topic
TOPIC_BINS = TOPIC_BASE + "bins"  # Topic for bin data

# --- Data File Paths ---
DATA_DIR = "generated_bin_data/"
BINS_JSON = os.path.join(DATA_DIR, "bins.json")


# --- Helper Functions ---
def read_json_data(filepath: str) -> list:
    """Reads data from a JSON file and returns a list of dictionaries."""
    data = []
    if os.path.exists(filepath):
        with open(filepath, mode='r', encoding='utf-8') as file:
            data = json.load(file)  # Load the entire JSON file
    return data


def publish_bin_data(client: mqtt.Client, topic: str, data: list):
    """Publishes a list of bin data dictionaries to the specified MQTT topic in parallel."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for bin_data in data:
            futures.append(executor.submit(client.publish, topic, json.dumps(bin_data)))
        for future in concurrent.futures.as_completed(futures):
            future.result()


# --- MQTT Callbacks ---
def on_connect(client, userdata, flags, rc):
    """Callback for when the client connects to the MQTT broker."""
    if rc == 0:
        print("Connected to MQTT broker.")
    else:
        print(f"Connection failed with code {rc}")


def on_disconnect(client, userdata, rc):
    """Callback for disconnection from the MQTT broker."""
    print(f"Disconnected from MQTT broker with code: {rc}")


# --- Main Function ---
def main():
    """Main function to connect to MQTT, publish bin data in parallel, and disconnect."""

    client = mqtt.Client()

    # Set up callbacks
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    # Connect to the MQTT broker
    print(f"Connecting to MQTT broker: {MQTT_BROKER_ADDRESS}:{MQTT_PORT}")
    client.connect(MQTT_BROKER_ADDRESS, MQTT_PORT, 60)
    client.loop_start()  # Start the MQTT loop in a separate thread

    time.sleep(5)  # Allow time for connection to establish

    # --- Publishing Logic ---

    bin_data = read_json_data(BINS_JSON)
    if bin_data:
        publish_bin_data(client, TOPIC_BINS, bin_data)
    else:
        print(f"No data found in {BINS_JSON}. Skipping bin data publishing.")

    # --- Disconnect ---
    print("\nFinished publishing bin data.")
    print("Disconnecting from MQTT broker.")
    client.loop_stop()
    client.disconnect()


if __name__ == "__main__":
    main()
