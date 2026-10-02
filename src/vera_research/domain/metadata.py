"""Domain models for location catalog metadata (cities and neighborhoods)."""

from dataclasses import dataclass, field
from typing import Iterator


@dataclass(frozen=True)
class Neighborhood:
    """Represents a neighborhood entity with display name and numeric ID."""

    name: str
    numeric_id: int


@dataclass(frozen=True)
class NeighborhoodCatalog:
    """First-class collection representing neighborhoods."""

    items: tuple[Neighborhood, ...] = field(default_factory=tuple)

    def __len__(self) -> int:
        """Return count of neighborhoods."""
        return len(self.items)

    def __iter__(self) -> Iterator[Neighborhood]:
        """Iterate over neighborhoods."""
        return iter(self.items)

    def __getitem__(self, index: int) -> Neighborhood:
        """Access a neighborhood by index."""
        return self.items[index]

    def find_by_id(self, numeric_id: int) -> Neighborhood | None:
        """Lookup neighborhood by numeric identifier."""
        for item in self.items:
            if item.numeric_id == numeric_id:
                return item
        return None

    def find_by_name(self, name: str) -> Neighborhood | None:
        """Lookup neighborhood by name."""
        clean_target = name.strip().lower()
        for item in self.items:
            if item.name.lower() == clean_target:
                return item
        return None


@dataclass(frozen=True)
class City:
    """Represents a municipality with name, numeric ID, and associated neighborhoods."""

    name: str
    numeric_id: int
    neighborhoods: NeighborhoodCatalog = field(default_factory=NeighborhoodCatalog)


@dataclass(frozen=True)
class CityCatalog:
    """First-class collection wrapping all available cities in the portal."""

    cities: tuple[City, ...] = field(default_factory=tuple)

    def __len__(self) -> int:
        """Return count of cities."""
        return len(self.cities)

    def __iter__(self) -> Iterator[City]:
        """Iterate over cities in catalog."""
        return iter(self.cities)

    def __getitem__(self, index: int) -> City:
        """Access a city by index."""
        return self.cities[index]

    def find_by_id(self, numeric_id: int) -> City | None:
        """Locate city by its numeric identifier."""
        for city in self.cities:
            if city.numeric_id == numeric_id:
                return city
        return None

    def find_by_name(self, name: str) -> City | None:
        """Locate city by name."""
        clean_target = name.strip().lower()
        for city in self.cities:
            if city.name.lower() == clean_target:
                return city
        return None
