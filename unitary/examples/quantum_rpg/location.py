from typing import Dict, List, Optional, Sequence

import dataclasses
import unitary.examples.quantum_rpg.encounter as encounter
import enum


class Direction(enum.Enum):
    NORTH = "north"
    EAST = "east"
    SOUTH = "south"
    WEST = "west"
    UP = "up"
    DOWN = "down"

    @classmethod
    def parse(cls, s: str) -> Optional["Direction"]:
        """Parses a string as a Direction.

        Allows prefixes, like 'e' to be parsed as EAST.
        """
        lower_s = s.lower()
        for d in Direction:
            if d.value.startswith(lower_s):
                return d


@dataclasses.dataclass
class Location:
    """Dataclass representing a location in the quantum RPG.

    Attributes:
        label: id of the location so that other rooms can
            refer to it succintly.
        title: Title or short description of the room.
        description: Longer description of the room.
        exits: Mapping from direction to label of the
           adjacent rooms.
        encounter: Sequence of encounters that can be
           visited here.

    """

    label: str
    title: str
    exits: Dict[Direction, str]
    encounters: Optional[List[encounter.Encounter]] = None
    description: Optional[str] = None

    def _exits(self) -> str:
        return ", ".join([ex.value for ex in self.exits]) + "."

    def remove_encounter(self, triggered_encounter) -> bool:
        self.encounters.remove(triggered_encounter)

    def print(self) -> str:
        return f"{self.title}\n\n{self.description}\nExits: {self._exits()}\n"


class World:
    """A list of connected locations that can be traversed.

    The first location is assumed to be the starting location.
    """

    def __init__(self, locations: Sequence[Location]):
        self.locations = {location.label: location for location in locations}
        self.current_location = locations[0]

    def move(self, direction: Direction) -> Optional[Location]:
        """Move to new location in the specified direction.

        If there is no room in that direction, returns None.
        """
        new_location = self.current_location.exits.get(direction, None)
        if new_location is not None:
            self.current_location = self.locations[new_location]
            return self.current_location
        return None
