# bin.py
import datetime
import json
import random
import time
from suburb_model.house import House
from suburb_model.location import Location

class bin:
    """
    A class to simulate data generation for a single smart dustbin,
    associated with a specific house.
    """

    def __init__(
        self,
        bin_id: str,
        house: House,  # Changed: Takes a House object
        initial_fill_level: float = 0.0,
        fill_rate_per_hour: float = 1.0,
        update_interval_seconds: int = 60,
        initial_status: str = "online",
        initial_temperature_celsius: float = 20.0,
        fill_variation_percentage: float = 0.5,
        temp_variation_celsius: float = 0.2,
    ):
        """
        Initializes the bin with a House object.
        """
        self.bin_id = bin_id
        self.house = house  # Store the House object
        self._fill_level_percentage = initial_fill_level
        self._fill_rate_per_hour = fill_rate_per_hour
        self._update_interval_seconds = update_interval_seconds
        self._status = initial_status
        self._temperature_celsius = initial_temperature_celsius
        self._fill_variation_percentage = fill_variation_percentage
        self._temp_variation_celsius = temp_variation_celsius

    def generate_data_point(self) -> dict:
        """
        Generates a simulated data point for the smart bin.
        """
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        # Get location from the associated house
        location = self.house.get_location().to_dict()  
        self._fill_level_percentage = min(
            100.0,
            max(
                0.0,
                self._fill_level_percentage
                + self._fill_rate_per_hour * (self._update_interval_seconds / 3600)
                + random.uniform(
                    -self._fill_variation_percentage, self._fill_variation_percentage
                ),
            ),
        )
        self._temperature_celsius += random.uniform(
            -self._temp_variation_celsius, self._temp_variation_celsius
        )
        return {
            "binId": self.bin_id,
            "timestamp": timestamp,
            "location": location,
            "fillLevelPercentage": round(self._fill_level_percentage, 2),
            "status": self._status,
            "temperatureCelsius": round(self._temperature_celsius, 2),
        }

    def get_bin_id(self) -> str:
        """Returns the bin's unique ID."""
        return self.bin_id

    def get_location(self) -> Location:
        """Returns the bin's Location object."""
        return self.house.get_location()  # Get location from house

    def get_house(self) -> House:
        """Returns the House object associated with the bin."""
        return self.house

    def get_status(self) -> str:
        """Returns the current simulated status of the bin."""
        return self._status

    def set_status(self, status: str):
        """Sets the simulated status of the bin."""
        self._status = status

if __name__ == "__main__":
    # Example Usage (can be run directly for testing)
    # Create location and house first
    example_loc = Location(-37.8136, 144.9631)
    example_house = House("1 Example St", example_loc, "house_example")

    # Create a simulator for a bin associated with the house
    melbourne_bin_simulator = bin(
        bin_id="MEL-CBD-001",
        house=example_house,  # Pass the house object
        initial_fill_level=10.0,
        fill_rate_per_hour=5.0,
        update_interval_seconds=5,
    )

    print(f"Starting simulation for Bin ID: {melbourne_bin_simulator.get_bin_id()}")
    print(f"Associated House: {melbourne_bin_simulator.get_house()}")
    print(f"Location: {melbourne_bin_simulator.get_location()}")

    try:
        # Generate data points over a short period
        for i in range(10):
            data_point = melbourne_bin_simulator.generate_data_point()
            print(json.dumps(data_point, indent=2))
            time.sleep(melbourne_bin_simulator._update_interval_seconds)

        # Simulate a status change
        melbourne_bin_simulator.set_status("low battery")
        print("\nSimulating status change...")
        data_point = melbourne_bin_simulator.generate_data_point()
        print(json.dumps(data_point, indent=2))

    except Exception as e:
        print(f"An error occurred: {e}")