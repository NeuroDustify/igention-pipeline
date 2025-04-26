# mqtt_publisher/publish_suburb_data.py
# Script to read generated suburb model data from CSVs and publish to MQTT.

import paho.mqtt.client as mqtt
import json
import csv
import os
import time
import sys # Keep sys for path manipulation if needed, though os handles it
from typing import List, Dict, Any

# --- MQTT Configuration ---
# Using the public Mosquitto broker which does not require authentication on port 1883
MQTT_BROKER_ADDRESS = "test.mosquitto.org"
MQTT_PORT = 1883 # Standard non-TLS MQTT port
# No username and password needed for this public broker

# --- MQTT Topics ---
# Define topics for each data type
# IMPORTANT: Use a unique prefix for public brokers to avoid conflicts!
# Replace 'your_unique_prefix' with something unique to your project.
TOPIC_BASE = "suburb/model/igention/" # Using the prefix you provided
TOPIC_DRIVEWAYS = TOPIC_BASE + "driveways"
TOPIC_HOUSES = TOPIC_BASE + "houses"
TOPIC_STREETS = TOPIC_BASE + "streets"
TOPIC_SUBURB = TOPIC_BASE + "suburb" # Note: Suburb data is likely a single message

# --- Data File Paths ---
# Data directory is relative to the project root (one level up from mqtt_publisher)
DATA_DIR = "../generated_data"
DRIVEWAYS_CSV = os.path.join(DATA_DIR, "driveways.csv")
HOUSES_CSV = os.path.join(DATA_DIR, "houses.csv")
STREETS_CSV = os.path.join(DATA_DIR, "streets.csv")
SUBURB_CSV = os.path.join(DATA_DIR, "suburb.csv")

# --- MQTT Client Callbacks ---

def on_connect(client, userdata, flags, rc):
    """Callback function for when the client connects to the MQTT broker."""
    # More detailed connection status reporting
    if rc == 0:
        print("Connection successful! Connected to MQTT Broker.")
        # You might want to set a flag here to indicate connection is ready
        # userdata['connected'] = True
    elif rc == 1:
        print("Connection failed: Incorrect protocol version.")
    elif rc == 2:
        print("Connection failed: Invalid client ID.")
    elif rc == 3:
        print("Connection failed: Server unavailable.")
    elif rc == 4:
        print("Connection failed: Bad username or password.") # Should not happen for public broker
    elif rc == 5:
        print("Connection failed: Not authorized.")
    else:
        print(f"Connection failed with return code: {rc}")

# The on_publish callback is useful for tracking message IDs, but not strictly needed for basic operation
# def on_publish(client, userdata, mid):
#     """Callback function for when a message is successfully published."""
#     print(f"Message published with MID {mid}")

def on_disconnect(client, userdata, rc):
    """Callback function for when the client disconnects from the MQTT broker."""
    if rc != 0:
        print(f"Disconnected from MQTT Broker with code: {rc} (unexpected)")
    else:
        print("Disconnected from MQTT Broker gracefully.")


# --- Data Reading Helper ---

def read_csv_data(filepath: str) -> List[Dict[str, str]]:
    """Reads data from a CSV file and returns a list of dictionaries."""
    # Adjust path to be relative to the script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level from mqtt_publisher to project root
    project_root = os.path.join(script_dir, os.pardir)
    absolute_filepath = os.path.join(project_root, filepath)

    if not os.path.exists(absolute_filepath):
        # print(f"Info: Data file not found at {absolute_filepath}. Skipping.") # Info level if file missing is expected
        return []
    try:
        with open(absolute_filepath, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            data = list(reader)
            # Basic check if CSV is empty but file exists
            if not data and os.path.getsize(absolute_filepath) > 0:
                 print(f"Warning: File {absolute_filepath} is not empty but contains no valid data rows (check headers?).")
            return data
    except Exception as e:
        print(f"Error reading CSV file {absolute_filepath}: {e}")
        return []

# --- Data Publishing Functions ---

def publish_data(client: mqtt.Client, topic: str, data: List[Dict[str, Any]]):
    """Publishes a list of data records to a given topic, one message per record."""
    if not client.is_connected():
        print(f"Client not connected. Cannot publish to {topic}.")
        return

    if not data:
        # This case is handled before calling publish_data, but good for robustness
        print(f"No data to publish for topic: {topic}")
        return

    print(f"\nPublishing {len(data)} records to topic: {topic}")
    for i, record in enumerate(data):
        payload = json.dumps(record)
        try:
            # Publish with QoS 1 (at least once delivery)
            # retain=False (message will not be retained by the broker after delivery)
            # Use publish with a timeout to wait for acknowledgement
            result = client.publish(topic, payload, qos=1, retain=False)
            result.wait_for_publish(timeout=5) # Wait up to 5 seconds for publish confirmation
            # print(f"  Published record {i+1}/{len(data)} (MID: {result.mid})") # Optional verbose output
            time.sleep(0.05) # Small delay between messages to avoid overwhelming broker/network
        except Exception as e:
            print(f"Error publishing record {i+1}/{len(data)} to {topic}: {e}")
            # Consider if you want to continue or stop on error

    print(f"Finished publishing {len(data)} records to {topic}")


def publish_single_message(client: mqtt.Client, topic: str, data: Dict[str, Any]):
    """Publishes a single data dictionary as one message to a given topic."""
    if not client.is_connected():
        print(f"Client not connected. Cannot publish to {topic}.")
        return

    if not data:
        # This case is handled before calling publish_single_message, but good for robustness
        print(f"No data to publish for topic: {topic}")
        return

    print(f"\nPublishing single message to topic: {topic}")
    payload = json.dumps(data)
    try:
        result = client.publish(topic, payload, qos=1, retain=False)
        result.wait_for_publish(timeout=5) # Wait up to 5 seconds for publish confirmation
        print(f"  Published message (MID: {result.mid})")
    except Exception as e:
        print(f"Error publishing single message to {topic}: {e}")


# --- Main Execution ---

def main():
    """
    Sets up MQTT client, connects, reads data from CSVs if available,
    publishes the data, and then disconnects.
    """
    print("Setting up MQTT client...")
    # Use a unique client ID, e.g., based on hostname and process ID
    client_id = f"python-suburb-publisher-{os.getpid()}"
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id) # Use API v2 and unique client ID
    client.on_connect = on_connect
    # client.on_publish = on_publish # Optional callback
    client.on_disconnect = on_disconnect

    # --- No TLS or username/password needed for test.mosquitto.org:1883 ---

    try:
        print(f"Attempting to connect to {MQTT_BROKER_ADDRESS}:{MQTT_PORT}...")
        # Increased connect timeout to 10 seconds for better robustness
        client.connect(MQTT_BROKER_ADDRESS, MQTT_PORT, 10) # Connect with a keepalive of 10 seconds (reduced from 60 for quicker exit)
    except Exception as e:
        print(f"An error occurred during the connection attempt: {e}")
        print("Please check your network connection, firewall, and the broker address/port.")
        print("Exiting.")
        return

    # Start the MQTT client loop in a non-blocking way to process callbacks
    client.loop_start()

    # Give the client time to connect. We wait until on_connect is likely called.
    print("Waiting for connection...")
    # A loop waiting for client.is_connected() is more reliable than a fixed sleep
    connect_timeout = 5 # seconds
    start_time = time.time()
    while not client.is_connected() and time.time() - start_time < connect_timeout:
        time.sleep(0.1)

    if not client.is_connected():
        print("\nConnection failed after waiting.")
        print("Possible reasons:")
        print("- Network issues or firewall blocking the connection.")
        print("- Incorrect broker address or port.")
        print("- Broker is down or unreachable.")
        print("Check the output above for any connection error messages.")
        print("Exiting.")
        client.loop_stop()
        return

    print("Connection established. Checking for data and publishing...")

    # --- Read and Publish Data from CSVs ---

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
    client.loop_stop() # Stop the network loop
    client.disconnect() # Send the DISCONNECT packet

    # Give the client a moment to disconnect gracefully
    time.sleep(1)

    print("Publisher script finished.")

# --- Script Entry Point ---
if __name__ == "__main__":
    main()
