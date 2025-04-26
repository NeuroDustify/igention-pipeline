# location.py
# Represents a geographical location

class Location:
    """
    Represents a geographical location with latitude and longitude.
    """
    def __init__(self, latitude: float, longitude: float):
        """
        Initializes a Location object.

        Args:
            latitude (float): The latitude coordinate.
            longitude (float): The longitude coordinate.
        """
        if not isinstance(latitude, (int, float)):
            raise TypeError("Latitude must be a number.")
        if not isinstance(longitude, (int, float)):
            raise TypeError("Longitude must be a number.")

        self.latitude: float = latitude
        self.longitude: float = longitude

    def __str__(self) -> str:
        """Returns a string representation of the location."""
        return f"Location(lat={self.latitude}, lon={self.longitude})"

    def __repr__(self) -> str:
        """Returns a developer-friendly string representation."""
        return f"Location(latitude={self.latitude}, longitude={self.longitude})"

    def __eq__(self, other) -> bool:
        """Checks if two Location objects are equal based on coordinates."""
        if not isinstance(other, Location):
            return False
        return self.latitude == other.latitude and self.longitude == other.longitude

    def to_dict(self) -> dict:
        """Returns the location as a dictionary."""
        return {"latitude": self.latitude, "longitude": self.longitude}

# Example Usage (optional)
if __name__ == "__main__":
    loc1 = Location(-37.8136, 144.9631)
    print(loc1)
    print(loc1.to_dict())

    loc2 = Location(-37.8136, 144.9631)
    print(loc1 == loc2) # Should be True
