# mqtt_publisher/publish_suburb_data.py
# Script to read generated suburb model data from CSVs and publish to MQTT.

import paho.mqtt.client as mqtt
import json
import csv
import os
import time
import sys  # Keep sys for path manipulation if needed, though os handles it
from typing import List, Dict, Any

# --- MQTT Configuration ---
# Using the public Mosquitto broker which does not require authentication on port 1883
MQTT_BROKER_ADDRESS = "test.mosquitto.org"
MQTT_PORT = 1883  # Standard non-TLS MQTT port
# No username and password needed for this public broker

# --- MQTT Topics ---
# Define topics for each data type
# IMPORTANT: Use a unique prefix for public brokers to avoid conflicts!
# Replace 'your_unique_prefix' with something unique to your project.
TOPIC_BASE = "suburb/model/igention/"  # Using the prefix you provided
TOPIC_DRIVEWAYS = TOPIC_BASE + "driveways"
TOPIC_HOUSES = TOPIC_BASE + "houses"
TOPIC_STREETS = TOPIC_BASE + "streets"
TOPIC_SUBURB = TOPIC_BASE + "suburb"  # Note: Suburb data is likely a single message

# --- Data File Paths ---
# Data directory is relative to the project root (one level up from mqtt_publisher)
DATA_DIR = "generated_suburb_data/"
DRIVEWAYS_CSV = os.path.join(DATA_DIR, "driveways.csv")
HOUSES_CSV = os.path.join(DATA_DIR, "houses.csv")
STREETS_CSV = os.path.join(DATA_DIR, "streets.csv")
SUBURB_CSV = os.path.join(DATA_DIR, "suburb.csv")


# --- Helper Functions ---
def read_csv_data(filepath: str) -> List[Dict[str, str]]:
    """Reads data from a CSV file and returns a list of dictionaries."""
    data = []
    if os.path.exists(filepath):
        with open(filepath, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
    return data


def publish_data(client: mqtt.Client, topic: str, data: List[Dict[str, Any]]):
    """Publishes a list of dictionaries to the specified MQTT topic."""
    for row in data:
        client.publish(topic, json.dumps(row))
        time.sleep(0.5)  # Throttle publishing


def publish_single_message(client: mqtt.Client, topic: str, data: Dict[str, Any]):
    """Publishes a single dictionary as a JSON message to the MQTT topic."""
    client.publish(topic, json.dumps(data))


# --- MQTT Callbacks ---
def on_connect(client, userdata, flags, rc):
    """Callback function for when the client connects to the MQTT broker."""
    if rc == 0:
        print("Connection established. Checking for data and publishing...")
    else:
        print(f"Connection failed with code {rc}")


def on_disconnect(client, userdata, rc):
    """Callback function for when the client disconnects from the MQTT broker."""
    print(f"Disconnected with result code '{rc}'")


# --- Main Function ---
def main():
    """Main function to connect to MQTT, publish data, and disconnect."""

    client = mqtt.Client()

    # Set up callbacks
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    # Connect to the MQTT broker
    print("Setting up MQTT client...")
    print(f"Attempting to connect to {MQTT_BROKER_ADDRESS}:{MQTT_PORT}...")
    client.connect(MQTT_BROKER_ADDRESS, MQTT_PORT, 60)
    client.loop_start()  # Start the network loop in a separate thread

    time.sleep(5)  # Give time for connection to establish

    # --- Publishing Logic ---
    # (Remains largely the same)

    # Publish Driveway Data
    driveway_data = read_csv_data(DRIVEWAYS_CSV)
    if driveway_data:
        publish_data(client, TOPIC_DRIVEWAYS, driveway_data)
    else:
        print(f"No data found in {DRIVEWAYS_CSV}. Skipping publishing for this topic.")

    # Publish House Data
    house_data = read_csv_data(HOUSES_CSV)
    if house_data:
        publish_data(client, TOPIC_HOUSES, house_data)
    else:
        print(f"No data found in {HOUSES_CSV}. Skipping publishing for this topic.")

    # Publish Street Data
    street_data = read_csv_data(STREETS_CSV)
    if street_data:
        publish_data(client, TOPIC_STREETS, street_data)
    else:
        print(f"No data found in {STREETS_CSV}. Skipping publishing for this topic.")

    # Publish Suburb Data (as a single message)
    suburb_data_list = read_csv_data(SUBURB_CSV)
    if suburb_data_list:
        # Assuming suburb data is just one row in the CSV
        publish_single_message(client, TOPIC_SUBURB, suburb_data_list[0])
    else:
        print(f"No data found in {SUBURB_CSV}. Skipping publishing for this topic.")

    # --- Disconnect ---
    print("\nFinished publishing available data.")
    print("Disconnecting from MQTT broker.")
    client.loop_stop()  # Stop the network loop
    client.disconnect()  # Send the DISCONNECT packet


if __name__ == "__main__":
    main()