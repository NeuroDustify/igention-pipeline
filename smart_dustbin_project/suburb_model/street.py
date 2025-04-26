# street.py
# Represents a street within the suburb

from typing import List, Optional
from .house import House
from .location import Location # Although street might not have a single point location, useful for segments

class Street:
    """
    Represents a street, containing multiple houses.
    """
    def __init__(self, name: str, street_id: str = None, houses: Optional[List[House]] = None):
        """
        Initializes a Street object.

        Args:
            name (str): The name of the street.
            street_id (str, optional): A unique identifier for the street. Defaults to None.
            houses (List[House], optional): A list of House objects located on the street.
                                           Defaults to None.
        """
        if not isinstance(name, str) or not name:
            raise ValueError("Street name must be a non-empty string.")
        if houses is not None and not all(isinstance(h, House) for h in houses):
             raise TypeError("Houses must be a list of House objects.")

        self.name: str = name
        self.street_id: str = street_id if street_id is not None else f"street_{id(self)}" # Simple unique ID
        self.houses: List[House] = houses if houses is not None else []
        # Could add attributes for street geometry (e.g., a list of Location points) in the future

    def __str__(self) -> str:
        """Returns a string representation of the street."""
        return f"Street(id={self.street_id}, name='{self.name}')"

    def __repr__(self) -> str:
        """Returns a developer-friendly string representation."""
        return f"Street(name='{self.name}', street_id='{self.street_id}', houses={repr(self.houses)})"

    def add_house(self, house: House):
        """Adds a house to the street."""
        if not isinstance(house, House):
            raise TypeError("Can only add House objects.")
        self.houses.append(house)

    def get_name(self) -> str:
        """Returns the name of the street."""
        return self.name

    def get_houses(self) -> List[House]:
        """Returns the list of houses on the street."""
        return self.houses

# Example Usage (optional)
if __name__ == "__main__":
    from .location import Location # Need relative import for example
    from .house import House # Need relative import for example

    street1 = Street("Main St", "main_st")

    house_loc1 = Location(-37.8140, 144.9640)
    house1 = House("123 Main St", house_loc1, "house_123")
    street1.add_house(house1)

    house_loc2 = Location(-37.8145, 144.9648)
    house2 = House("456 Main St", house_loc2, "house_456")
    street1.add_house(house2)

    print(street1)
    print(f"Houses on {street1.get_name()}: {[h.get_address() for h in street1.get_houses()]}")
