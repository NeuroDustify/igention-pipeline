# mqtt_publisher/publish_suburb_data.py
# Script to read generated suburb model data from CSVs and publish to MQTT in parallel.

import paho.mqtt.client as mqtt
import json
import csv
import os
import time
import sys
import concurrent.futures
from typing import List, Dict, Any, Tuple

# --- MQTT Configuration ---
MQTT_BROKER_ADDRESS = "test.mosquitto.org"
MQTT_PORT = 1883

# --- MQTT Topics ---
TOPIC_BASE = "suburb/model/igention/"
TOPIC_DRIVEWAYS = TOPIC_BASE + "driveways"
TOPIC_HOUSES = TOPIC_BASE + "houses"
TOPIC_STREETS = TOPIC_BASE + "streets"
TOPIC_SUBURB = TOPIC_BASE + "suburb"

# --- Data File Paths ---
DATA_DIR = "generated_suburb_data/"
DRIVEWAYS_CSV = os.path.join(DATA_DIR, "driveways.csv")
HOUSES_CSV = os.path.join(DATA_DIR, "houses.csv")
STREETS_CSV = os.path.join(DATA_DIR, "streets.csv")
SUBURB_CSV = os.path.join(DATA_DIR, "suburb.csv")

# --- Helper Functions ---
def read_csv_data(filepath: str) -> List[Dict[str, str]]:
    data = []
    if os.path.exists(filepath):
        try:
            with open(filepath, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                data = list(reader)
        except FileNotFoundError:
            print(f"Error: File not found at {filepath}")
        except Exception as e:
            print(f"Error reading CSV file {filepath}: {e}")
    else:
        print(f"Warning: File not found at {filepath}. Skipping.")
    return data

def format_location_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for row in data:
        if 'latitude' in row and 'longitude' in row:
            row['location'] = {
                "latitude": float(row.pop('latitude')),
                "longitude": float(row.pop('longitude'))
            }
    return data

def publish_data(client: mqtt.Client, topic: str, data: List[Dict[str, Any]]):
    total_count = len(data)
    if total_count == 0:
        print(f"No data to publish for topic {topic}. Skipping.")
        return

    print(f"Starting to publish {total_count} messages to topic {topic}...")
    count = 0
    for row in data:
        try:
            client.publish(topic, json.dumps(row))
            count += 1
            percent_complete = round((count / total_count) * 100, 2)
            print(f"\rPublishing to topic {topic}: {count}/{total_count} ({percent_complete}%)", end="", flush=True)
            time.sleep(0.01)
        except Exception as e:
            print(f"\nError publishing message to {topic}: {row}. Error: {e}")

    print(f"\nFinished publishing {total_count} messages to topic {topic}.")

def publish_parallel_data(client: mqtt.Client, data_tasks: List[Tuple[str, str]]):
    print("Starting parallel data publishing...")
    futures_list = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        for topic, filepath in data_tasks:
            data = read_csv_data(filepath)
            data = format_location_data(data)
            if data:
                future = executor.submit(publish_data, client, topic, data)
                futures_list.append((future, topic))
            else:
                print(f"No data found in {filepath}. Skipping publishing for topic {topic}.")

        for future, topic in futures_list:
            try:
                future.result()
            except Exception as e:
                print(f"Error during parallel publishing for topic {topic}: {e}")

    print("Parallel data publishing finished.")

def publish_single_message(client: mqtt.Client, topic: str, data: Dict[str, Any]):
    try:
        client.publish(topic, json.dumps(data))
        print(f"Published single message to topic {topic}.")
    except Exception as e:
        print(f"Error publishing single message to {topic}: {e}")

# --- MQTT Callbacks ---
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT Connection established.")
    else:
        print(f"MQTT Connection failed with code {rc}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"Unexpected disconnection from MQTT broker. Result code: {rc}")
    else:
        print("Disconnected from MQTT broker.")

# --- Main Function ---
def main():
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    print("Setting up MQTT client...")
    print(f"Attempting to connect to {MQTT_BROKER_ADDRESS}:{MQTT_PORT}...")
    try:
        client.connect(MQTT_BROKER_ADDRESS, MQTT_PORT, 60)
    except ConnectionRefusedError:
        print("Connection refused. Is the broker running and accessible?")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred during connection: {e}")
        sys.exit(1)

    client.loop_start()

    print("Waiting for connection...")
    time.sleep(3)
    if not client.is_connected():
        print("MQTT client failed to connect. Exiting.")
        client.loop_stop()
        sys.exit(1)

    parallel_tasks = [
        (TOPIC_DRIVEWAYS, DRIVEWAYS_CSV),
        (TOPIC_HOUSES, HOUSES_CSV),
        (TOPIC_STREETS, STREETS_CSV),
    ]

    publish_parallel_data(client, parallel_tasks)

    suburb_data_list = read_csv_data(SUBURB_CSV)
    suburb_data_list = format_location_data(suburb_data_list)
    if suburb_data_list:
        if suburb_data_list:
            publish_single_message(client, TOPIC_SUBURB, suburb_data_list[0])
        else:
            print(f"Suburb CSV {SUBURB_CSV} was read but appears empty.")
    else:
        print(f"No data found in {SUBURB_CSV}. Skipping publishing for this topic.")

    print("\nFinished publishing available data.")
    print("Stopping MQTT network loop and disconnecting.")
    client.loop_stop()
    client.disconnect()
    print("MQTT client disconnected.")

if __name__ == "__main__":
    main()
