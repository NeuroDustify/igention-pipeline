import os
import sys
import json
import random
import csv
from typing import List, Dict, Any

try:
    from smartbin_model.bin import bin
    from suburb_model.house import House
    from suburb_model.location import Location
except ImportError as e:
    try:
        from smartbin_model.bin import bin
        from suburb_model.house import House
        from suburb_model.location import Location
    except ImportError as e_inner:
        print(f"Error importing modules: {e_inner}")
        print("Please ensure 'bin.py', 'house.py', and 'location.py' are accessible.")
        exit(1)

DATA_DIR = "generated_bin_data"
BINS_JSON = os.path.join(DATA_DIR, "bins.json")
HOUSES_CSV = "generated_suburb_data/houses.csv"

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def write_json(filepath: str, data: List[Dict[str, Any]]):
    ensure_data_dir()
    with open(filepath, mode="w", encoding="utf-8") as outfile:
        json.dump(data, outfile, indent=4)
    print(f"Data successfully written to {filepath}")

def read_houses_from_csv(filepath: str) -> Dict[str, House]:
    """Reads house data from CSV, with robust error handling for column names."""

    houses = {}
    try:
        with open(filepath, mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            header = reader.fieldnames  # Get the header row
            print(f"CSV Header: {header}")  # Print the header for debugging

            # **Robustly find latitude and longitude columns:**
            latitude_key = None
            longitude_key = None
            for key in header:
                lower_key = key.lower()  # Case-insensitive comparison
                if "lat" in lower_key:
                    latitude_key = key
                elif "lon" in lower_key:
                    longitude_key = key
                if latitude_key and longitude_key:
                    break  # Found both, no need to continue searching

            if not latitude_key or not longitude_key:
                raise ValueError(
                    "Could not find latitude or longitude columns in CSV."
                    "Please ensure columns like 'latitude', 'longitude', 'lat', or 'lon' (or similar) exist."
                )

            for row in reader:
                address = row["address"]  # Assuming 'address' is always there
                latitude = float(row[latitude_key])
                longitude = float(row[longitude_key])
                property_id = row["property_id"]  # Assuming 'property_id' is always there
                location = Location(latitude, longitude)
                house = House(address, location, property_id)
                houses[property_id] = house

    except FileNotFoundError:
        print(f"Error: CSV file not found at {filepath}")
    except KeyError as e:
        print(f"Error: Column not found in CSV: {e}")
        print("Please check the column names in your CSV file and update the script accordingly.")
        print("Common issues: Case sensitivity, typos, or incorrect column names.")
    except ValueError as e:
        print(f"Error processing CSV data: {e}")
    return houses


def generate_bin_data(num_bins: int):
    """Generates simulated SmartBin data associated with houses from CSV."""

    print("\n--- Generate SmartBin Data ---")

    houses = read_houses_from_csv(HOUSES_CSV)
    if not houses:
        print("Error: No house data loaded. Cannot generate bin data.")
        return

    bin_data = []
    print("Generating smart bin data (simulated)...")

    house_ids = list(houses.keys())
    num_houses = len(house_ids)

    for i in range(num_bins):
        bin_id = f"BIN-{i+1:03}"
        house = houses[house_ids[i % num_houses]]
        bin_simulator = bin(
            bin_id=bin_id,
            house=house,
            initial_fill_level=random.uniform(0.0, 20.0),
            fill_rate_per_hour=random.uniform(2.0, 8.0),
            update_interval_seconds=60 + random.randint(-10, 10),
            initial_temperature_celsius=random.uniform(15.0, 25.0),
        )
        data_point = bin_simulator.generate_data_point()
        bin_data.append(data_point)

    write_json(BINS_JSON, bin_data)

def view_generated_data():
    """Displays a summary of generated bin data."""
    print("\n--- Generated SmartBin Data Summary ---")
    if os.path.exists(BINS_JSON):
        with open(BINS_JSON, "r", encoding="utf-8") as infile:
            data = json.load(infile)
        print(f"SmartBins: {len(data)} records found in {BINS_JSON}")
        if data:
            print("  Sample record (Location derived from the assigned house):")
            print(json.dumps(data[0], indent=4))
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
        print("1. Generate SmartBin Data (using houses.csv)")
        print("2. View Generated Data")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            num_bins = int(input("Enter the number of smart bins to simulate: "))
            generate_bin_data(num_bins)
        elif choice == "2":
            view_generated_data()
        elif choice == "3":
            print("Exiting data generator.")
            break
        else:
            print("Invalid choice. Please try again.")

# --- Script Entry Point ---
if __name__ == "__main__":
    ensure_data_dir()
    main_menu()