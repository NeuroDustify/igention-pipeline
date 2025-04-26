# driveway.py
# Represents a driveway associated with a house

from .location import Location

class Driveway:
    """
    Represents a driveway, typically an access point for bin placement.
    """
    def __init__(self, location: Location, identifier: str = None):
        """
        Initializes a Driveway object.

        Args:
            location (Location): The geographical location of the driveway access point.
            identifier (str, optional): A unique identifier for the driveway if needed.
                                        Defaults to None.
        """
        if not isinstance(location, Location):
            raise TypeError("Location must be a Location object.")

        self.location: Location = location
        self.identifier: str = identifier if identifier is not None else f"driveway_{id(self)}" # Simple unique ID

    def __str__(self) -> str:
        """Returns a string representation of the driveway."""
        return f"Driveway(id={self.identifier}, location={self.location})"

    def __repr__(self) -> str:
        """Returns a developer-friendly string representation."""
        return f"Driveway(location={repr(self.location)}, identifier='{self.identifier}')"

    def get_location(self) -> Location:
        """Returns the location of the driveway."""
        return self.location

    def get_identifier(self) -> str:
        """Returns the unique identifier of the driveway."""
        return self.identifier

# Example Usage (optional)
if __name__ == "__main__":
    from .location import Location # Need relative import for example

    driveway_loc = Location(-37.8150, 144.9650)
    driveway1 = Driveway(driveway_loc, "123_Main_St_Driveway")
    print(driveway1)
    print(driveway1.get_location())
