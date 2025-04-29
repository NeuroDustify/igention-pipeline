# mqtt_publisher/publish_suburb_data.py
# Script to read generated suburb model data from CSVs and publish to MQTT in parallel.

import paho.mqtt.client as mqtt
import json
import csv
import os
import time
import sys
import concurrent.futures  # For parallel execution
from typing import List, Dict, Any, Tuple

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
        try:
            with open(filepath, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                # Convert data types if necessary (e.g., numbers from strings)
                # This example keeps them as strings, but you might add conversion here
                data = list(reader) # Directly convert DictReader iterator to list
        except FileNotFoundError:
             print(f"Error: File not found at {filepath}")
        except Exception as e:
            print(f"Error reading CSV file {filepath}: {e}")
    else:
        print(f"Warning: File not found at {filepath}. Skipping.")
    return data


def publish_data(client: mqtt.Client, topic: str, data: List[Dict[str, Any]]):
    """Publishes a list of dictionaries to the specified MQTT topic."""
    total_count = len(data)
    if total_count == 0:
        print(f"No data to publish for topic {topic}. Skipping.")
        return

    print(f"Starting to publish {total_count} messages to topic {topic}...")
    count = 0
    for row in data:
        try:
            # Ensure data is JSON serializable - might need conversion if not
            client.publish(topic, json.dumps(row))
            count += 1
            percent_complete = round((count / total_count) * 100, 2)
            # Use carriage return to update the same line
            print(f"\rPublishing to topic {topic}: {count}/{total_count} ({percent_complete}%)", end="", flush=True)
            time.sleep(0.01)  # Small throttle to avoid overwhelming broker/network
        except Exception as e:
            print(f"\nError publishing message to {topic}: {row}. Error: {e}")
            # Decide whether to continue or break on error

    print(f"\nFinished publishing {total_count} messages to topic {topic}.")


def publish_parallel_data(client: mqtt.Client, data_tasks: List[Tuple[str, str]]):
    """Publishes data from multiple CSV files in parallel to the specified MQTT topics."""
    print("Starting parallel data publishing...")
    futures_list = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor: # Using a few workers
        for topic, filepath in data_tasks:
            data = read_csv_data(filepath)
            if data:
                # Submit the publish_data function to the executor
                future = executor.submit(publish_data, client, topic, data)
                futures_list.append((future, topic)) # Keep track of the topic for error reporting
            else:
                print(f"No data found in {filepath}. Skipping publishing for topic {topic}.")

        # Wait for all futures to complete and check for exceptions
        for future, topic in futures_list:
            try:
                future.result() # This will re-raise any exception caught in the thread
            except Exception as e:
                print(f"Error during parallel publishing for topic {topic}: {e}")

    print("Parallel data publishing finished.")


def publish_single_message(client: mqtt.Client, topic: str, data: Dict[str, Any]):
    """Publishes a single dictionary as a JSON message to the MQTT topic."""
    try:
        client.publish(topic, json.dumps(data))
        print(f"Published single message to topic {topic}.")
    except Exception as e:
        print(f"Error publishing single message to {topic}: {e}")


# --- MQTT Callbacks ---
def on_connect(client, userdata, flags, rc):
    """Callback function for when the client connects to the MQTT broker."""
    if rc == 0:
        print("MQTT Connection established.")
    else:
        print(f"MQTT Connection failed with code {rc}")
        # Depending on error code, you might want to exit or retry
        # sys.exit(f"Connection failed: {rc}") # Example of exiting on failure


def on_disconnect(client, userdata, rc):
    """Callback function for when the client disconnects from the MQTT broker."""
    if rc != 0:
        print(f"Unexpected disconnection from MQTT broker. Result code: {rc}")
    else:
        print("Disconnected from MQTT broker.")


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
    # Use a loop for robust connection attempt in a real application
    try:
        client.connect(MQTT_BROKER_ADDRESS, MQTT_PORT, 60)
    except ConnectionRefusedError:
        print("Connection refused. Is the broker running and accessible?")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred during connection: {e}")
        sys.exit(1)


    client.loop_start()  # Start the network loop in a separate thread

    # Wait for connection to be established. Use on_connect for better state management.
    # This sleep is a simple approach for this script.
    print("Waiting for connection...")
    time.sleep(3)
    if not client.is_connected():
         print("MQTT client failed to connect. Exiting.")
         client.loop_stop()
         sys.exit(1)


    # --- Publishing Logic using the Parallel function ---

    # Define the tasks for parallel publishing (multi-message topics)
    parallel_tasks = [
        (TOPIC_DRIVEWAYS, DRIVEWAYS_CSV),
        (TOPIC_HOUSES, HOUSES_CSV),
        (TOPIC_STREETS, STREETS_CSV),
    ]

    # Execute the parallel publishing for the defined tasks
    publish_parallel_data(client, parallel_tasks)

    # --- Publish Suburb Data (as a single message) ---
    # This is handled separately as it's typically one large message, not a stream.
    suburb_data_list = read_csv_data(SUBURB_CSV)
    if suburb_data_list:
        # Assuming suburb data is just one row in the CSV
        if suburb_data_list: # Check again if the list is not empty after read
             # Publish the first (and likely only) row as a single message
             publish_single_message(client, TOPIC_SUBURB, suburb_data_list[0])
        else:
             print(f"Suburb CSV {SUBURB_CSV} was read but appears empty.")
    else:
        print(f"No data found in {SUBURB_CSV}. Skipping publishing for this topic.")


    # --- Disconnect ---
    print("\nFinished publishing available data.")
    print("Stopping MQTT network loop and disconnecting.")
    client.loop_stop()  # Stop the network loop
    client.disconnect() # Send the DISCONNECT packet
    print("MQTT client disconnected.")


if __name__ == "__main__":
    main()