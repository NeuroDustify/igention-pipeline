import csv
import os
import random
import time
from typing import List, Dict, Any

# Assume suburb_model directory is in the same directory as this script
# and contains location.py, driveway.py, house.py, street.py, suburb.py
try:
    from suburb_model.location import Location
    from suburb_model.driveway import Driveway
    from suburb_model.house import House
    from suburb_model.street import Street
    from suburb_model.suburb import Suburb
except ImportError:
    print("Error: Could not import suburb model classes.")
    print("Please ensure the 'suburb_model' directory is in the same location")
    print("as this script and contains the necessary Python files.")
    exit(1)

# --- Configuration ---
DATA_DIR = "generated_suburb_data"
DRIVEWAYS_CSV = os.path.join(DATA_DIR, "driveways.csv")
HOUSES_CSV = os.path.join(DATA_DIR, "houses.csv")
STREETS_CSV = os.path.join(DATA_DIR, "streets.csv")
SUBURB_CSV = os.path.join(DATA_DIR, "suburb.csv")

# --- Helper Functions ---

def ensure_data_dir():
    """Ensures the data directory exists."""
    os.makedirs(DATA_DIR, exist_ok=True)

def read_csv(filepath: str) -> List[Dict[str, str]]:
    """Reads data from a CSV file and returns a list of dictionaries."""
    if not os.path.exists(filepath):
        return []
    with open(filepath, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        return list(reader)

def write_csv(filepath: str, data: List[Dict[str, Any]], fieldnames: List[str]):
    """Writes data (list of dictionaries) to a CSV file."""
    ensure_data_dir()
    with open(filepath, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"Data successfully written to {filepath}")

def generate_unique_id(prefix: str) -> str:
    """Generates a simple unique ID using timestamp and random number."""
    return f"{prefix}_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"

# --- Data Generation Functions ---

def generate_driveways():
    """Generates simulated Driveway data and saves to CSV."""
    print("\n--- Generate Driveway Data ---")
    num_driveways = input("Enter the number of driveways to simulate: ")
    try:
        num_driveways = int(num_driveways)
        if num_driveways <= 0:
            print("Number of driveways must be positive.")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    driveway_data = []
    print("Generating driveway locations (simulated)...")
    # Simulate locations within a general area (e.g., based on Melbourne CBD range)
    # In a real scenario, you'd get these from a map tool or actual data
    base_lat = -37.81
    base_lon = 144.96
    lat_range = 0.02
    lon_range = 0.03

    for i in range(num_driveways):
        driveway_id = generate_unique_id("driveway")
        # Simulate location slightly varied
        lat = base_lat + random.uniform(-lat_range/2, lat_range/2)
        lon = base_lon + random.uniform(-lon_range/2, lon_range/2)
        location = Location(lat, lon)

        driveway_data.append({
            "driveway_id": driveway_id,
            "latitude": location.latitude,
            "longitude": location.longitude
        })

    fieldnames = ["driveway_id", "latitude", "longitude"]
    write_csv(DRIVEWAYS_CSV, driveway_data, fieldnames)

def generate_houses():
    """Generates simulated House data and saves to CSV."""
    print("\n--- Generate House Data ---")

    # Check for dependency: Driveways
    driveway_data = read_csv(DRIVEWAYS_CSV)
    if not driveway_data:
        print("Dependency missing: No driveway data found.")
        print("Please generate Driveway data first using option 2.")
        return

    num_houses = input(f"Enter the number of houses to simulate (max {len(driveway_data)} suggested): ")
    try:
        num_houses = int(num_houses)
        if num_houses <= 0:
            print("Number of houses must be positive.")
            return
        if num_houses > len(driveway_data):
             print(f"Warning: Number of houses ({num_houses}) is more than available driveways ({len(driveway_data)}).")
             print("Some houses will not be assigned a driveway.")

    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    house_data = []
    available_driveway_ids = [d['driveway_id'] for d in driveway_data]
    used_driveway_ids = set()

    print("Generating house data (simulated addresses and locations)...")

    # Simulate house locations near driveways
    # In a real scenario, you'd get actual addresses and locations
    street_names = ["Main St", "Oak Ave", "Elm Cres", "Pine Ln", "Maple Pde"] # Example names

    for i in range(num_houses):
        property_id = generate_unique_id("house")
        address_number = i + 1
        street_name = random.choice(street_names)
        address = f"{address_number} {street_name}"

        # Assign a driveway if available and not already used by this house
        assigned_driveway_id = None
        if available_driveway_ids:
             # Simple assignment logic: try to assign one driveway per house
             # In a real scenario, this mapping would be based on real data
             potential_driveways = [d for d in driveway_data if d['driveway_id'] not in used_driveway_ids]
             if potential_driveways:
                 chosen_driveway = random.choice(potential_driveways)
                 assigned_driveway_id = chosen_driveway['driveway_id']
                 used_driveway_ids.add(assigned_driveway_id)
                 # Simulate house location close to the assigned driveway
                 house_lat = float(chosen_driveway['latitude']) + random.uniform(-0.0005, 0.0005)
                 house_lon = float(chosen_driveway['longitude']) + random.uniform(-0.0005, 0.0005)
                 location = Location(house_lat, house_lon)
             else:
                 # If all driveways are used, simulate a location without a specific driveway link
                 print(f"Warning: Not enough unique driveways for house {i+1}. Simulating location without driveway link.")
                 base_lat = -37.81
                 base_lon = 144.96
                 lat_range = 0.02
                 lon_range = 0.03
                 house_lat = base_lat + random.uniform(-lat_range/2, lat_range/2)
                 house_lon = base_lon + random.uniform(-lon_range/2, lon_range/2)
                 location = Location(house_lat, house_lon)

        else:
             # If no driveway data exists (shouldn't happen if dependency check works, but as fallback)
             print(f"Warning: No driveway data available. Simulating location without driveway link for house {i+1}.")
             base_lat = -37.81
             base_lon = 144.96
             lat_range = 0.02
             lon_range = 0.03
             house_lat = base_lat + random.uniform(-lat_range/2, lat_range/2)
             house_lon = base_lon + random.uniform(-lon_range/2, lon_range/2)
             location = Location(house_lat, house_lon)


        house_data.append({
            "property_id": property_id,
            "address": address,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "driveway_ids": assigned_driveway_id if assigned_driveway_id else "" # Store assigned driveway ID
        })

    fieldnames = ["property_id", "address", "latitude", "longitude", "driveway_ids"]
    write_csv(HOUSES_CSV, house_data, fieldnames)


def generate_streets():
    """Generates simulated Street data and saves to CSV."""
    print("\n--- Generate Street Data ---")

    # Check for dependency: Houses
    house_data = read_csv(HOUSES_CSV)
    if not house_data:
        print("Dependency missing: No house data found.")
        print("Please generate House data first using option 3.")
        return

    num_streets = input(f"Enter the number of streets to simulate (max {len(house_data)} suggested): ")
    try:
        num_streets = int(num_streets)
        if num_streets <= 0:
            print("Number of streets must be positive.")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    street_data = []
    all_house_ids = [h['property_id'] for h in house_data]
    random.shuffle(all_house_ids) # Shuffle to distribute houses randomly

    # Simple assignment: Divide houses roughly equally among streets
    houses_per_street = len(all_house_ids) // num_streets if num_streets > 0 else 0
    remaining_houses = len(all_house_ids) % num_streets

    start_index = 0
    street_names = ["Main St", "Oak Ave", "Elm Cres", "Pine Ln", "Maple Pde", "Currawong Ct", "Ironbark Ct", "Bramley Pl", "Warranwah Dr", "Condon St", "Marnie Rd", "Kiandra Way", "Tatiana Close", "Regency Pl", "Greenwood Dr", "Inorom Pl", "Langford Rd", "Vincent Dr", "Bambara Close", "Parade E", "Strathfieldsaye Rd"] # More names based on image

    if num_streets > len(street_names):
        print(f"Warning: Generating more streets ({num_streets}) than available unique names ({len(street_names)}). Names will repeat.")
        # Extend street names list by repeating if needed
        while len(street_names) < num_streets:
            street_names.extend(["Street" + str(i) for i in range(num_streets)]) # Fallback generic names

    random.shuffle(street_names) # Shuffle names

    for i in range(num_streets):
        street_id = generate_unique_id("street")
        street_name = street_names[i % len(street_names)] # Use modulo for repeating names

        # Assign houses to this street
        current_street_house_count = houses_per_street + (1 if i < remaining_houses else 0)
        end_index = start_index + current_street_house_count
        assigned_house_ids = all_house_ids[start_index:end_index]
        start_index = end_index

        street_data.append({
            "street_id": street_id,
            "name": street_name,
            "house_ids": ",".join(assigned_house_ids) # Store house IDs as comma-separated string
        })

    fieldnames = ["street_id", "name", "house_ids"]
    write_csv(STREETS_CSV, street_data, fieldnames)


def generate_suburb():
    """Generates simulated Suburb data and saves to CSV."""
    print("\n--- Generate Suburb Data ---")

    # Check for dependency: Streets
    street_data = read_csv(STREETS_CSV)
    if not street_data:
        print("Dependency missing: No street data found.")
        print("Please generate Street data first using option 4.")
        return

    suburb_name = input("Enter the name of the suburb (e.g., South Morang): ")
    if not suburb_name:
        print("Suburb name cannot be empty.")
        return

    suburb_id = generate_unique_id("suburb")
    all_street_ids = [s['street_id'] for s in street_data]

    suburb_data = [{
        "suburb_id": suburb_id,
        "name": suburb_name,
        "street_ids": ",".join(all_street_ids) # Store street IDs as comma-separated string
    }]

    fieldnames = ["suburb_id", "name", "street_ids"]
    write_csv(SUBURB_CSV, suburb_data, fieldnames)


def view_generated_data():
    """Displays a summary of generated data."""
    print("\n--- Generated Data Summary ---")
    files = {
        "Driveways": DRIVEWAYS_CSV,
        "Houses": HOUSES_CSV,
        "Streets": STREETS_CSV,
        "Suburb": SUBURB_CSV
    }
    for name, filepath in files.items():
        data = read_csv(filepath)
        print(f"{name}: {len(data)} records found in {filepath}")
        if data:
            print("  Sample record:", data[0])
        else:
            print("  No data generated yet.")
    print("-" * 30)


# --- Main Menu ---

def main_menu():
    """Displays the main menu and handles user input."""
    while True:
        print("\n--- Suburb Data Generator Menu ---")
        print("1. View Generated Data Summary")
        print("2. Generate Driveway Data")
        print("3. Generate House Data")
        print("4. Generate Street Data")
        print("5. Generate Suburb Data")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            view_generated_data()
        elif choice == '2':
            generate_driveways()
        elif choice == '3':
            generate_houses()
        elif choice == '4':
            generate_streets()
        elif choice == '5':
            generate_suburb()
        elif choice == '6':
            print("Exiting data generator.")
            break
        else:
            print("Invalid choice. Please try again.")

# --- Script Entry Point ---

if __name__ == "__main__":
    ensure_data_dir() # Ensure data directory exists on startup
    main_menu()
