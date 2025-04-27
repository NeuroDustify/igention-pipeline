# main.py
# (Rest of your code, including imports)

import sys
import os

# Add the project root directory to the Python path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Import the necessary modules
try:
    from scripts import generate_bin_data
    from scripts import generate_suburb_data
    from mqtt_publisher import publish_suburb_data
    from mqtt_subscriber import subscribe_data  # Import the subscriber
except ImportError as e:
    print(f"Error importing project modules: {e}")
    print("Please ensure you are running this script from the project root directory.")
    print("Also, check that the subdirectories exist and contain the necessary files.")
    sys.exit(1)


def display_main_menu():
    """Displays the main project menu."""
    print("\n--- Smart Dustbin Project Menu ---")
    print("1. Run Bin Data Generator")
    print("2. Run Suburb Data Generator")
    print("3. Run MQTT Publisher")
    print("4. Run MQTT Subscriber")  # NEW: Option to run the subscriber
    print("5. Exit")
    print("-" * 35)


def main():
    """Main function to run the project menu."""
    while True:
        display_main_menu()
        choice = input("Enter your choice: ")

        if choice == '1':
            print("\nStarting Bin Data Generator...")
            generate_bin_data.main_menu()
            print("\nBin Data Generator finished.")
        elif choice == '2':
            print("\nStarting Suburb Data Generator...")
            generate_suburb_data.main_menu()
            print("\nSuburb Data Generator finished.")
        elif choice == '3':
            print("\nStarting MQTT Publisher...")
            publish_suburb_data.main()
            print("\nMQTT Publisher finished.")
        elif choice == '4':
            print("\nStarting MQTT Subscriber...")
            subscribe_data.main()  # Call the subscriber's main function
            print("\nMQTT Subscriber is running... (It will keep running until interrupted)")
        elif choice == '5':
            print("Exiting Smart Dustbin Project.")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()