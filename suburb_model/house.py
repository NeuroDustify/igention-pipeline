# house.py
# Represents an individual house/property

from typing import List, Optional
from .location import Location
from .driveway import Driveway

class House:
    """
    Represents an individual house or property.
    """
    def __init__(self,
                 address: str,
                 location: Location,
                 property_id: str = None,
                 driveways: Optional[List[Driveway]] = None):
        """
        Initializes a House object.

        Args:
            address (str): The street address of the house.
            location (Location): The geographical location of the house (e.g., centroid).
            property_id (str, optional): A unique identifier for the property.
                                         Defaults to None.
            driveways (List[Driveway], optional): A list of Driveway objects associated
                                                 with the house. Defaults to None.
        """
        if not isinstance(address, str) or not address:
            raise ValueError("Address must be a non-empty string.")
        if not isinstance(location, Location):
            raise TypeError("Location must be a Location object.")
        if driveways is not None and not all(isinstance(d, Driveway) for d in driveways):
             raise TypeError("Driveways must be a list of Driveway objects.")


        self.address: str = address
        self.location: Location = location
        self.property_id: str = property_id if property_id is not None else f"prop_{id(self)}" # Simple unique ID
        self.driveways: List[Driveway] = driveways if driveways is not None else []

    def __str__(self) -> str:
        """Returns a string representation of the house."""
        return f"House(id={self.property_id}, address='{self.address}')"

    def __repr__(self) -> str:
        """Returns a developer-friendly string representation."""
        return f"House(address='{self.address}', location={repr(self.location)}, property_id='{self.property_id}', driveways={repr(self.driveways)})"

    def add_driveway(self, driveway: Driveway):
        """Adds a driveway to the house."""
        if not isinstance(driveway, Driveway):
            raise TypeError("Can only add Driveway objects.")
        self.driveways.append(driveway)

    def get_address(self) -> str:
        """Returns the address of the house."""
        return self.address

    def get_location(self) -> Location:
        """Returns the geographical location of the house."""
        return self.location

    def get_driveways(self) -> List[Driveway]:
        """Returns the list of driveways associated with the house."""
        return self.driveways

# Example Usage (optional)
if __name__ == "__main__":
    from .location import Location # Need relative import for example
    from .driveway import Driveway # Need relative import for example

    house_loc = Location(-37.8140, 144.9640)
    house1 = House("123 Main St", house_loc, "house_123")

    driveway_loc1 = Location(-37.8141, 144.9642)
    driveway1 = Driveway(driveway_loc1)
    house1.add_driveway(driveway1)

    print(house1)
    print(house1.get_driveways())
