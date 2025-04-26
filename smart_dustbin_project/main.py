# main.py
# Main entry point for the Smart Dustbin Project.
# Provides a menu to access different project functionalities.

import sys
import os

# Add the project root directory to the Python path
# This allows importing modules from subdirectories like scripts and mqtt_publisher
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Import the main functions from the scripts and mqtt_publisher modules
try:
    # Updated import path for the data generator script
    from scripts import generate_bin_data
    from scripts import generate_suburb_data
    from mqtt_publisher import publish_suburb_data
except ImportError as e:
    print(f"Error importing project modules: {e}")
    print("Please ensure you are running this script from the project root directory")
    print("(the directory containing main.py and the other subfolders).")
    print("Also, check that the subdirectories (suburb_model, scripts, mqtt_publisher, generated_data)")
    print("exist and contain the necessary files, including __init__.py where applicable.")
    sys.exit(1)


def display_main_menu():
    """Displays the main project menu."""
    print("\n--- Smart Dustbin Project Menu ---")
    print("1. Run Bin Data Generator")
    print("2. Run Suburb Data Generator")
    print("3. Run MQTT Publisher")
    print("4. Exit")
    print("-" * 35)

def main():
    """Main function to run the project menu."""
    while True:
        display_main_menu()
        choice = input("Enter your choice: ")

        if choice == '1':
            print("\nStarting Bin Data Generator...")
            # Call the main menu function from the data_generator script
            generate_bin_data.main_menu()
            print("\nBin Data Generator finished.")
        elif choice == '2':
            print("\nStarting Suburb Data Generator...")
            # Call the main menu function from the data_generator script
            generate_suburb_data.main_menu()
            print("\nSuburb Data Generator finished.")
        elif choice == '3':
            print("\nStarting MQTT Publisher...")
            # Call the main function from the mqtt_publisher script
            publish_suburb_data.main()
            print("\nMQTT Publisher finished.")
        elif choice == '4':
            print("Exiting Smart Dustbin Project.")
            break
        else:
            print("Invalid choice. Please try again.")

# --- Script Entry Point ---
if __name__ == "__main__":
    main()
