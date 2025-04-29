# generate_bin_file.py

import os
import sys
import json
import random
import csv # Need csv to read houses.csv
from typing import List, Dict, Any

# --- Configure Paths ---
# Assuming the script is in a 'scripts' directory and models/data are in parent dirs
SCRIPT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.join(SCRIPT_DIR, '..')

# Adjust model import path based on your project structure
# This import path matches the user's provided code structure ('smartbin_model.bin')
try:
    # Add the project root to sys.path to import from subdirectories like smartbin_model
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)

    from smartbin_model.bin import bin as SmartBin # Renamed to avoid conflict with built-in bin()
    print("Successfully imported SmartBin class.")

except ImportError:
    print("\n---------------------------------------------------------")
    print("IMPORT ERROR:")
    print("Could not import the 'bin' class from 'smartbin_model'.")
    print("Please ensure you have a directory structure like:")
    print("  your_project_root/")
    print("  ├── scripts/")
    print(f"  │   └── {os.path.basename(__file__)}")
    print("  └── smartbin_model/")
    print("      └── bin.py")
    print("\nAnd that you are running the script from the 'scripts' directory or the project root.")
    print("\nPython is currently looking in these directories (sys.path):")
    for path in sys.path:
        print(f"  {path}")
    print("---------------------------------------------------------\n")
    sys.exit(1)

# Define data directories relative to the project root
DATA_DIR_HOUSES = os.path.join(PROJECT_ROOT, "generated_suburb_data") # Where houses.csv is expected
DATA_DIR_BINS = os.path.join(PROJECT_ROOT, "generated_bin_data") # Where bins.json will be saved

HOUSES_CSV_PATH = os.path.join(DATA_DIR_HOUSES, "houses.csv")
BINS_JSON_PATH = os.path.join(DATA_DIR_BINS, "bins.json")


# --- Helper Functions ---

def ensure_data_dir(directory: str):
    """Ensures the specified data directory exists."""
    os.makedirs(directory, exist_ok=True)

def read_houses_from_csv(filepath: str) -> List[Dict[str, Any]]:
    """
    Reads house data from a CSV file, expecting 'property_id', 'latitude', 'longitude'.
    Converts latitude and longitude to floats.
    """
    houses_data = []
    if not os.path.exists(filepath):
        print(f"Error: House data file not found at {filepath}")
        return []

    try:
        with open(filepath, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            # Check for essential columns
            required_fields = ['property_id', 'latitude', 'longitude']
            if not all(field in reader.fieldnames for field in required_fields):
                missing = [field for field in required_fields if field not in reader.fieldnames]
                print(f"Error: CSV file {filepath} is missing required columns: {missing}")
                return []

            for row in reader:
                # Create a copy of the row to avoid modifying the original DictReader row
                processed_row = dict(row)
                try:
                    # Attempt to convert location to float
                    processed_row['latitude'] = float(processed_row.get('latitude'))
                    processed_row['longitude'] = float(processed_row.get('longitude'))
                    # Use provided ID (checked by required_fields)
                    property_id = processed_row.get('property_id')

                    # Basic validation for essential fields after processing
                    if property_id is None or processed_row['latitude'] is None or processed_row['longitude'] is None:
                         print(f"Warning: Skipping row due to missing/invalid required data: {row}")
                         continue

                    houses_data.append(processed_row) # Append the processed dictionary
                except (ValueError, TypeError):
                    print(f"Warning: Could not parse latitude/longitude for row: {row}. Skipping row.")
                    continue
                except Exception as e:
                    print(f"Warning: Error processing row: {row}. Error: {e}. Skipping row.")
                    continue

    except Exception as e:
        print(f"An error occurred while reading CSV file {filepath}: {e}")
        return []

    print(f"Successfully read {len(houses_data)} houses from {filepath}.")
    return houses_data


def write_json(filepath: str, data: List[Dict[str, Any]]):
    """Writes data (list of dictionaries) to a JSON file."""
    # Ensure the directory for this specific file exists
    directory = os.path.dirname(filepath)
    ensure_data_dir(directory)

    try:
        with open(filepath, mode='w', encoding='utf-8') as outfile:
            json.dump(data, outfile, indent=4)  # Pretty-print JSON
        print(f"Data successfully written to {filepath}")
    except Exception as e:
        print(f"Error writing data to {filepath}: {e}")


def generate_bin_data():
    """
    Reads house data, generates simulated SmartBin data for each house (up to
    the number of houses available), and saves it to a JSON file.
    """
    print("\n--- Generate SmartBin Data ---")

    # 1. Read house data
    all_houses_data = read_houses_from_csv(HOUSES_CSV_PATH)

    if not all_houses_data:
        print("No valid house data found. Cannot generate bins.")
        return

    num_available_houses = len(all_houses_data)
    print(f"Found {num_available_houses} houses available in {HOUSES_CSV_PATH}.")

    # 2. Get desired number of bins from user input and validate
    while True:
        try:
            user_input = input(f"Enter the desired number of smart bins to generate (0 to {num_available_houses}): ")
            num_bins_to_create = int(user_input)
            if num_bins_to_create >= 0: # Allow 0
                 break
            else:
                 print("Please enter a non-negative integer.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

    if num_bins_to_create > num_available_houses:
        print(f"Warning: Cannot generate {num_bins_to_create} bins. Only {num_available_houses} houses available.")
        print("Generating bins for all available houses instead.")
        num_bins_to_create = num_available_houses # Cap the number

    if num_bins_to_create == 0:
        print("No bins requested (number of bins is 0).")
        return

    # 3. Generate bins for the selected number of houses
    bin_data_list_for_json = []
    print(f"Generating {num_bins_to_create} smart bin(s) linked to houses...")

    # Select the houses for which bins will be created (take the first N)
    houses_to_assign_bins = all_houses_data[:num_bins_to_create]

    for i, house in enumerate(houses_to_assign_bins):
        try:
            # Get house details
            house_id = house.get('property_id')
            latitude = house.get('latitude')
            longitude = house.get('longitude')

            # Double-check essential data is present after selection
            if house_id is None or latitude is None or longitude is None:
                 print(f"Warning: Skipping bin creation for house data with missing info: {house}. Index: {i}")
                 continue

            # Create unique bin ID linked to the house ID
            bin_id = f"BIN_{house_id}"

            # Create a bin instance using the house's location
            bin_simulator = SmartBin(
                bin_id=bin_id,
                latitude=latitude,
                longitude=longitude,
                # Add random initial state to bins
                initial_fill_level=random.uniform(0.0, 20.0),
                fill_rate_per_hour=random.uniform(2.0, 8.0),
                update_interval_seconds=60, # Or random.randint(50, 70) for variation
                initial_temperature_celsius=random.uniform(15.0, 25.0),
            )

            # Generate an initial data point from the bin simulator
            # We modify this data point slightly to include the linked house ID
            data_point = bin_simulator.generate_data_point()
            data_point['linkedHouseId'] = house_id # Add the link back to the house

            bin_data_list_for_json.append(data_point)

        except Exception as e:
            print(f"Error creating bin for house ID {house.get('property_id', 'Unknown')}. Error: {e}. Skipping.")
            continue

    # 4. Write the generated data to JSON
    write_json(BINS_JSON_PATH, bin_data_list_for_json)
    print(f"Generated {len(bin_data_list_for_json)} bin records for {len(houses_to_assign_bins)} houses.")


def view_generated_data():
    """Displays a summary and sample of generated bin data from JSON."""

    print("\n--- Generated SmartBin Data Summary ---")
    if os.path.exists(BINS_JSON_PATH):
        try:
            with open(BINS_JSON_PATH, 'r', encoding='utf-8') as infile:
                data = json.load(infile)
            print(f"SmartBins: {len(data)} records found in {BINS_JSON_PATH}")
            if data:
                print("  Sample record:")
                # Pretty-print the first record, including the linkedHouseId
                print(json.dumps(data[0], indent=4))
            else:
                print("  The bins.json file is empty.")
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {BINS_JSON_PATH}. File might be corrupted.")
        except Exception as e:
            print(f"An error occurred while reading {BINS_JSON_PATH}: {e}")
    else:
        print(f"  {BINS_JSON_PATH} not found. No data generated yet.")
    print("-" * 30)


# --- Main Menu ---

def main_menu():
    """Displays the main menu and handles user input."""
    # Ensure the base data directories exist on startup
    ensure_data_dir(DATA_DIR_HOUSES) # This is where the input CSV is expected
    ensure_data_dir(DATA_DIR_BINS)   # This is where the output JSON goes

    # Create a dummy houses.csv if it doesn't exist, to avoid immediate error
    # in read_houses_from_csv if running for the first time.
    if not os.path.exists(HOUSES_CSV_PATH):
        print(f"'{os.path.basename(HOUSES_CSV_PATH)}' not found in '{DATA_DIR_HOUSES}'. Creating a dummy file.")
        dummy_data = [
            ['property_id', 'address', 'latitude', 'longitude'],
            ['house_001', '1 Example St', -37.81, 144.96],
            ['house_002', '2 Example Ave', -37.8105, 144.9605],
            ['house_003', '3 Example Ln', -37.811, 144.961],
        ]
        try:
            ensure_data_dir(DATA_DIR_HOUSES) # Ensure parent dir exists
            with open(HOUSES_CSV_PATH, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(dummy_data)
            print(f"Dummy '{os.path.basename(HOUSES_CSV_PATH)}' created with {len(dummy_data)-1} records.")
            print("Please replace this with your actual house data.")
        except Exception as e:
            print(f"Error creating dummy houses.csv: {e}")


    while True:
        print("\n--- SmartBin Data Generator Menu ---")
        print("1. Generate SmartBin Data (from houses.csv)")
        print("2. View Generated Bin Data (from bins.json)")
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
    main_menu()