"""Domain entities and first-class collection for property search listings."""

from collections.abc import Iterator
from dataclasses import dataclass, field
from urllib.parse import unquote, urlsplit


@dataclass(frozen=True)
class ListingIdentity:
    """Identification and source and canonical links for a property."""

    property_id: str
    url_path: str
    url: str = ""


@dataclass(frozen=True)
class ListingLocation:
    """Geographic information parsed from a listing."""

    neighborhood: str
    city: str
    state: str = "MG"


@dataclass(frozen=True)
class ListingSpecs:
    """Property specifications parsed from search card."""

    bedrooms: int = 0
    bathrooms: int = 0
    parking_spaces: int = 0


@dataclass(frozen=True)
class ListingSummary:
    """Summary of a property listing card returned from search."""

    identity: ListingIdentity
    title: str
    location: ListingLocation
    price_text: str
    price_numeric: float | None
    specs: ListingSpecs
    thumbnail_url: str | None = None


@dataclass(frozen=True)
class ListingCollection:
    """First-class collection wrapping search results and pagination status."""

    items: tuple[ListingSummary, ...] = field(default_factory=tuple)
    current_page: int = 1
    has_next_page: bool = False

    def __len__(self) -> int:
        """Return the number of listings in this page."""
        return len(self.items)

    def __iter__(self) -> Iterator[ListingSummary]:
        """Iterate over the listing items."""
        return iter(self.items)

    def __getitem__(self, index: int) -> ListingSummary:
        """Access a listing by index."""
        return self.items[index]

    def is_empty(self) -> bool:
        """Check if collection contains no items."""
        return len(self.items) == 0

    def filter_by_bedrooms(self, count: int) -> "ListingCollection":
        """Filter items by exact bedroom count."""
        matched = tuple(item for item in self.items if item.specs.bedrooms == count)
        return ListingCollection(items=matched, current_page=self.current_page, has_next_page=self.has_next_page)

    def filter_by_min_bedrooms(self, count: int) -> "ListingCollection":
        """Filter items having at least the given bedroom count."""
        matched = tuple(item for item in self.items if item.specs.bedrooms >= count)
        return ListingCollection(items=matched, current_page=self.current_page, has_next_page=self.has_next_page)

    def to_dictionary(self) -> dict:
        """Serialize listings while preserving native pagination metadata."""
        return {
            "listings": [self._serialize_listing(item) for item in self.items],
            "current_page": self.current_page,
            "has_next_page": self.has_next_page,
        }

    def _validate_public_url(self, listing: ListingSummary) -> None:
        """Reject absent, relative, and non-property listing URLs."""
        property_id = listing.identity.property_id
        try:
            parsed_url = urlsplit(listing.identity.url)
        except ValueError as exc:
            raise ValueError(
                f"Invalid public property URL for listing {property_id}"
            ) from exc
        is_property_route = parsed_url.path.startswith(f"/imovel/{property_id}/")
        is_fallback_route = parsed_url.path == f"/imovel/{property_id}.html"
        is_absolute = parsed_url.scheme in {"http", "https"} and bool(parsed_url.netloc)
        has_dot_segments = self._has_dot_segments(parsed_url.path)
        if not is_absolute or has_dot_segments or not (is_property_route or is_fallback_route):
            raise ValueError(
                f"A valid absolute public property URL is required for listing {property_id}"
            )

    def _has_dot_segments(self, path: str) -> bool:
        decoded_path = unquote(path)
        return any(segment in {".", ".."} for segment in decoded_path.split("/"))

    def _serialize_listing(self, listing: ListingSummary) -> dict:
        """Convert one typed listing to its public payload."""
        self._validate_public_url(listing)
        return {
            "property_id": listing.identity.property_id,
            "url_path": listing.identity.url_path,
            "url": listing.identity.url,
            "title": listing.title,
            "neighborhood": listing.location.neighborhood,
            "city": listing.location.city,
            "state": listing.location.state,
            "price_text": listing.price_text,
            "price_numeric": listing.price_numeric,
            "bedrooms": listing.specs.bedrooms,
            "bathrooms": listing.specs.bathrooms,
            "parking_spaces": listing.specs.parking_spaces,
            "thumbnail_url": listing.thumbnail_url,
        }
