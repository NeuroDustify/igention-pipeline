# suburb.py
# Represents the entire suburb area

from typing import List, Optional
from .street import Street
from .house import House # Import House to potentially get all houses easily

class Suburb:
    """
    Represents an entire suburb area, containing multiple streets.
    """
    def __init__(self, name: str, suburb_id: str = None, streets: Optional[List[Street]] = None):
        """
        Initializes a Suburb object.

        Args:
            name (str): The name of the suburb.
            suburb_id (str, optional): A unique identifier for the suburb. Defaults to None.
            streets (List[Street], optional): A list of Street objects within the suburb.
                                            Defaults to None.
        """
        if not isinstance(name, str) or not name:
            raise ValueError("Suburb name must be a non-empty string.")
        if streets is not None and not all(isinstance(s, Street) for s in streets):
             raise TypeError("Streets must be a list of Street objects.")

        self.name: str = name
        self.suburb_id: str = suburb_id if suburb_id is not None else f"suburb_{id(self)}" # Simple unique ID
        self.streets: List[Street] = streets if streets is not None else []
        # Could add boundaries (e.g., a polygon of Location points) in the future

    def __str__(self) -> str:
        """Returns a string representation of the suburb."""
        return f"Suburb(id={self.suburb_id}, name='{self.name}')"

    def __repr__(self) -> str:
        """Returns a developer-friendly string representation."""
        return f"Suburb(name='{self.name}', suburb_id='{self.suburb_id}', streets={repr(self.streets)})"

    def add_street(self, street: Street):
        """Adds a street to the suburb."""
        if not isinstance(street, Street):
            raise TypeError("Can only add Street objects.")
        self.streets.append(street)

    def get_name(self) -> str:
        """Returns the name of the suburb."""
        return self.name

    def get_streets(self) -> List[Street]:
        """Returns the list of streets in the suburb."""
        return self.streets

    def get_all_houses(self) -> List[House]:
        """Returns a flattened list of all houses in the suburb."""
        all_houses = []
        for street in self.streets:
            all_houses.extend(street.get_houses())
        return all_houses


# Example Usage (optional)
if __name__ == "__main__":
    from .location import Location # Need relative import for example
    from .driveway import Driveway # Need relative import for example
    from .house import House # Need relative import for example
    from .street import Street # Need relative import for example

    # Create some houses and driveways
    house1_loc = Location(-37.8140, 144.9640)
    driveway1_loc = Location(-37.8141, 144.9642)
    driveway1 = Driveway(driveway1_loc, "123_Main_St_Driveway")
    house1 = House("123 Main St", house1_loc, "house_123", driveways=[driveway1])

    house2_loc = Location(-37.8145, 144.9648)
    house2 = House("456 Main St", house2_loc, "house_456") # No driveway specified initially

    # Create a street and add houses
    street1 = Street("Main St", "main_st", houses=[house1, house2])

    # Create the suburb and add the street
    suburb1 = Suburb("Example Suburb", "example_suburb_id", streets=[street1])

    print(suburb1)
    print(f"Streets in {suburb1.get_name()}: {[s.get_name() for s in suburb1.get_streets()]}")
    print(f"All houses in {suburb1.get_name()}: {[h.get_address() for h in suburb1.get_all_houses()]}")
