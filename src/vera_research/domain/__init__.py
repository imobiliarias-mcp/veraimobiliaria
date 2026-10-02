"""Domain models and interfaces for Vera Imobiliária rental research."""

from vera_research.domain.criteria import (
    LocationCriteria,
    SearchCriteria,
    SearchScope,
)
from vera_research.domain.enums import CityId, PropertyType, TransactionType
from vera_research.domain.listing import (
    ListingCollection,
    ListingIdentity,
    ListingLocation,
    ListingSpecs,
    ListingSummary,
)
from vera_research.domain.metadata import (
    City,
    CityCatalog,
    Neighborhood,
    NeighborhoodCatalog,
)
from vera_research.domain.property import (
    PhotoGallery,
    PropertyDetail,
    PropertyLocation,
    PropertyOverview,
    PropertyPricing,
    PropertySpecs,
)
from vera_research.domain.values import PageNumber, PriceRange, RoomCount

__all__ = [
    "City",
    "CityCatalog",
    "CityId",
    "ListingCollection",
    "ListingIdentity",
    "ListingLocation",
    "ListingSpecs",
    "ListingSummary",
    "LocationCriteria",
    "Neighborhood",
    "NeighborhoodCatalog",
    "PageNumber",
    "PhotoGallery",
    "PriceRange",
    "PropertyDetail",
    "PropertyLocation",
    "PropertyOverview",
    "PropertyPricing",
    "PropertySpecs",
    "PropertyType",
    "RoomCount",
    "SearchCriteria",
    "SearchScope",
    "TransactionType",
]
