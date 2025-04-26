import os
import sys # You might need this if you use the sys.path.append fix
import json
import random  # Import the random module
from typing import List, Dict, Any

# Assume suburb_model directory is in the same directory as this script
# and contains location.py, driveway.py, house.py, street.py, suburb.py
try:
    from smartbin_model.bin import bin
except ImportError:
    print("Error: Could not import Bin class from smartbin_model.")
    print("Please ensure the 'smartbin_model' directory is in the same location")
    print("as this script and contains the necessary Python files.")
    exit(1)

# --- Configuration ---
DATA_DIR = "generated_bin_data"
BINS_JSON = os.path.join(DATA_DIR, "bins.json")  # Using JSON to store bin data

# --- Helper Functions ---

def ensure_data_dir():
    """Ensures the data directory exists."""
    os.makedirs(DATA_DIR, exist_ok=True)

def write_json(filepath: str, data: List[Dict[str, Any]]):
    """Writes data (list of dictionaries) to a JSON file."""
    ensure_data_dir()
    with open(filepath, mode='w', encoding='utf-8') as outfile:
        json.dump(data, outfile, indent=4)  # Pretty-print JSON
    print(f"Data successfully written to {filepath}")

def generate_bin_data():
    """
    Generates simulated SmartBin data and saves it to a JSON file.
    """
    print("\n--- Generate SmartBin Data ---")
    num_bins = input("Enter the number of smart bins to simulate: ")
    try:
        num_bins = int(num_bins)
        if num_bins <= 0:
            print("Number of bins must be positive.")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    bin_data = []
    print("Generating smart bin data (simulated)...")

    # Simulate bin locations within a general area
    base_lat = -37.81  # Example: Melbourne
    base_lon = 144.96
    lat_range = 0.02
    lon_range = 0.03

    for i in range(num_bins):
        bin_id = f"BIN-{i+1:03}"  # Simple bin ID (e.g., BIN-001)
        # Simulate location slightly varied
        lat = base_lat + random.uniform(-lat_range/2, lat_range/2)
        lon = base_lon + random.uniform(-lon_range/2, lon_range/2)

        # Create a bin instance
        bin_simulator = bin(
            bin_id=bin_id,
            latitude=lat,
            longitude=lon,
            initial_fill_level=random.uniform(0.0, 20.0),  # Start with some random fill
            fill_rate_per_hour=random.uniform(2.0, 8.0),    # Random fill rate
            update_interval_seconds=60 + random.randint(-10, 10), # Vary update interval a bit
            initial_temperature_celsius=random.uniform(15.0, 25.0), # Random temp
        )

        # Generate initial data point
        data_point = bin_simulator.generate_data_point()
        bin_data.append(data_point)

    write_json(BINS_JSON, bin_data)


def view_generated_data():
    """Displays a summary of generated bin data."""

    print("\n--- Generated SmartBin Data Summary ---")
    if os.path.exists(BINS_JSON):
        with open(BINS_JSON, 'r', encoding='utf-8') as infile:
            data = json.load(infile)
        print(f"SmartBins: {len(data)} records found in {BINS_JSON}")
        if data:
            print("  Sample record:")
            print(json.dumps(data[0], indent=4))  # Pretty-print the first record
        else:
            print("  No data generated yet.")
    else:
        print("  No data generated yet.")
    print("-" * 30)


# --- Main Menu ---

def main_menu():
    """Displays the main menu and handles user input."""
    while True:
        print("\n--- SmartBin Data Generator Menu ---")
        print("1. Generate SmartBin Data")
        print("2. View Generated Data")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            generate_bin_data()
        elif choice == '2':
            view_generated_data()
        elif choice == '3':
            print("Exiting data generator.")
            break
        else:
            print("Invalid choice. Please try again.")

# --- Script Entry Point ---

if __name__ == "__main__":
    ensure_data_dir()  # Ensure data directory exists on startup
    main_menu()
