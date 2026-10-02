"""Domain models for full property details and photo gallery collection."""

from dataclasses import dataclass, field
from typing import Iterator


@dataclass(frozen=True)
class PhotoGallery:
    """First-class collection representing a property's photo image URLs."""

    photo_urls: tuple[str, ...] = field(default_factory=tuple)
    high_res_urls: tuple[str, ...] = field(default_factory=tuple)

    def __len__(self) -> int:
        """Return total number of photos in gallery."""
        return len(self.photo_urls)

    def __iter__(self) -> Iterator[str]:
        """Iterate over photo URLs."""
        return iter(self.photo_urls)

    def __getitem__(self, index: int) -> str:
        """Get photo URL by index."""
        return self.photo_urls[index]

    def first_photo(self) -> str | None:
        """Return the primary photo URL if available."""
        if not self.photo_urls:
            return None
        return self.photo_urls[0]

    def first_high_res_photo(self) -> str | None:
        """Return the primary high-resolution photo URL if available."""
        if not self.high_res_urls:
            return None
        return self.high_res_urls[0]


@dataclass(frozen=True)
class PropertyLocation:
    """Detailed geographic location of a property."""

    address: str
    neighborhood: str
    city: str
    state: str = "MG"
    map_url: str = ""


@dataclass(frozen=True)
class PropertyPricing:
    """Price and additional fee details."""

    amount: float | None
    currency: str = "BRL"
    formatted_text: str = ""
    iptu_text: str = ""
    condominio_text: str = ""


@dataclass(frozen=True)
class PropertySpecs:
    """Room counts and dimensions for property details."""

    bedrooms: int = 0
    bathrooms: int = 0
    parking_spaces: int = 0
    built_area: str = ""
    lot_area: str = ""


@dataclass(frozen=True)
class PropertyOverview:
    """Identity and textual description of the property."""

    property_id: str
    title: str
    description: str = ""


@dataclass(frozen=True)
class PropertyDetail:
    """Complete detail view of a real estate property."""

    overview: PropertyOverview
    pricing: PropertyPricing
    location: PropertyLocation
    specs: PropertySpecs
    features: tuple[str, ...] = field(default_factory=tuple)
    photos: PhotoGallery = field(default_factory=PhotoGallery)
    canonical_url: str = ""
