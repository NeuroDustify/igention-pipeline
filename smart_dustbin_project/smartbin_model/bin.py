import datetime
import json
import random
import time

class bin:
    """
    A class to simulate data generation for a single smart dustbin.

    This class is designed to be decoupled, allowing it to be used
    independently in various projects for testing or simulation purposes.
    It generates data points resembling those from a real smart bin sensor.
    """

    def __init__(self,
                 bin_id: str,
                 latitude: float,
                 longitude: float,
                 initial_fill_level: float = 0.0,
                 fill_rate_per_hour: float = 1.0, # Average percentage points increase per hour
                 update_interval_seconds: int = 60, # How often data is generated
                 initial_status: str = "online",
                 initial_temperature_celsius: float = 20.0,
                 fill_variation_percentage: float = 0.5, # Max random variation in fill per interval
                 temp_variation_celsius: float = 0.2 # Max random variation in temp per interval
                ):
        """
        Initializes the bin for a specific bin.

        Parameters:
            bin_id (str): A unique identifier for the bin.
            latitude (float): The geographical latitude of the bin's location.
            longitude (float): The geographical longitude of the bin's location.
            initial_fill_level (float): Starting fill level percentage (0.0 to 100.0).
                                        Defaults to 0.0.
            fill_rate_per_hour (float): The average rate at which the bin fills
                                        in percentage points per hour. Defaults to 1.0.
            update_interval_seconds (int): The time interval in seconds between
                                           generated data points. Defaults to 60 (1 minute).
            initial_status (str): The initial operational status of the bin.
                                  Defaults to "online".
            initial_temperature_celsius (float): The initial temperature inside the bin.
                                                 Defaults to 20.0.
            fill_variation_percentage (float): Maximum random percentage points
                                               to add/subtract to fill level per interval.
                                               Defaults to 0.5.
            temp_variation_celsius (float): Maximum random degrees Celsius to add/subtract
                                            to temperature per interval. Defaults to 0.2.
        """
        if not 0.0 <= initial_fill_level <= 100.0:
            raise ValueError("initial_fill_level must be between 0.0 and 100.0")
        if update_interval_seconds <= 0:
             raise ValueError("update_interval_seconds must be positive")

        self._bin_id = bin_id
        self._latitude = latitude
        self._longitude = longitude
        self._fill_level = initial_fill_level
        self._fill_rate_per_second = fill_rate_per_hour / 3600.0 # Convert rate to per second
        self._update_interval_seconds = update_interval_seconds
        self._status = initial_status
        self._temperature_celsius = initial_temperature_celsius
        self._fill_variation_percentage = fill_variation_percentage
        self._temp_variation_celsius = temp_variation_celsius

        self._last_update_time = datetime.datetime.now(datetime.timezone.utc)

    def generate_data_point(self) -> dict:
        """
        Generates a single simulated data point for the bin based on the
        current state and time elapsed.

        Simulates the fill level increasing over time with some random variation,
        and also simulates temperature variation.

        Returns:
            dict: A dictionary containing the simulated bin data in a
                  JSON-like structure.
        """
        current_time = datetime.datetime.now(datetime.timezone.utc)
        time_elapsed = (current_time - self._last_update_time).total_seconds()

        # Simulate fill level increase with variation
        fill_increase = time_elapsed * self._fill_rate_per_second
        random_fill_variation = random.uniform(-self._fill_variation_percentage, self._fill_variation_percentage)
        self._fill_level += fill_increase + random_fill_variation

        # Ensure fill level stays within 0 and 100
        self._fill_level = max(0.0, min(100.0, self._fill_level))

        # Simulate temperature variation
        random_temp_variation = random.uniform(-self._temp_variation_celsius, self._temp_variation_celsius)
        self._temperature_celsius += random_temp_variation

        # Update the last update time
        self._last_update_time = current_time

        # Construct the data payload
        data_payload = {
            "binId": self._bin_id,
            "timestamp": current_time.isoformat(),
            "location": {
                "latitude": self._latitude,
                "longitude": self._longitude
            },
            "fillLevelPercentage": round(self._fill_level, 2), # Round for cleaner output
            "status": self._status,
            "temperatureCelsius": round(self._temperature_celsius, 2) # Round for cleaner output
        }

        return data_payload

    def get_bin_id(self) -> str:
        """Returns the unique identifier of the bin."""
        return self._bin_id

    def get_location(self) -> tuple[float, float]:
        """Returns the location of the bin as a tuple (latitude, longitude)."""
        return (self._latitude, self._longitude)

    def get_current_fill_level(self) -> float:
        """Returns the current simulated fill level percentage."""
        return self._fill_level

    def get_status(self) -> str:
        """Returns the current simulated status of the bin."""
        return self._status

    def set_status(self, status: str):
        """Sets the simulated status of the bin."""
        self._status = status

# Example Usage (can be run directly for testing)
if __name__ == "__main__":
    # Create a simulator for a bin in Melbourne
    melbourne_bin_simulator = bin(
        bin_id="MEL-CBD-001",
        latitude=-37.8136,
        longitude=144.9631,
        initial_fill_level=10.0,
        fill_rate_per_hour=5.0, # Fills relatively quickly for demonstration
        update_interval_seconds=5 # Generate data every 5 seconds
    )

    print(f"Starting simulation for Bin ID: {melbourne_bin_simulator.get_bin_id()}")
    print(f"Location: {melbourne_bin_simulator.get_location()}")

    try:
        # Generate data points over a short period
        for i in range(10):
            data_point = melbourne_bin_simulator.generate_data_point()
            print(json.dumps(data_point, indent=2)) # Print as formatted JSON
            time.sleep(melbourne_bin_simulator._update_interval_seconds) # Wait for the next interval

        # Simulate a status change
        melbourne_bin_simulator.set_status("low battery")
        print("\nSimulating status change...")
        data_point = melbourne_bin_simulator.generate_data_point()
        print(json.dumps(data_point, indent=2))

    except KeyboardInterrupt:
        print("\nSimulation stopped manually.")