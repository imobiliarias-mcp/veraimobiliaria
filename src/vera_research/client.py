"""Central rental research MCP interface and client."""

from vera_research.collaborators import RentalNetworkGateway, RentalParserSuite
from vera_research.domain.criteria import SearchCriteria
from vera_research.domain.enums import CityId, PropertyType
from vera_research.domain.listing import ListingCollection
from vera_research.domain.metadata import CityCatalog, NeighborhoodCatalog
from vera_research.domain.property import PhotoGallery, PropertyDetail


class VeraRentalClient:
    """Central rental research client serving as the project's MCP interface."""

    def __init__(
        self,
        gateway: RentalNetworkGateway | None = None,
        parsers: RentalParserSuite | None = None,
    ) -> None:
        """Initialize client with gateway and parser suite collaborators."""
        self._gateway = gateway or RentalNetworkGateway()
        if parsers is not None:
            self._parsers = parsers
            return
        public_base_url = self._configured_public_base_url()
        self._parsers = RentalParserSuite(public_base_url=public_base_url)

    def _configured_public_base_url(self) -> str | None:
        public_base_url = getattr(self._gateway, "public_base_url", None)
        if public_base_url is None:
            return None
        return public_base_url()

    def search(self, criteria: SearchCriteria, apply_bedroom_filter: bool = False) -> ListingCollection:
        """Execute search query and return parsed collection of listings."""
        resp = self._gateway.fetch_search(criteria)
        parser = self._parsers.search_parser
        collection = parser.parse(resp.text, page_number=criteria.page.value)
        if not apply_bedroom_filter or criteria.bedrooms.count == 0:
            return collection
        return collection.filter_by_min_bedrooms(criteria.bedrooms.count)

    def search_rentals(
        self,
        city_id: int = int(CityId.TIMOTEO),
        property_type: PropertyType = PropertyType.TODOS,
        neighborhood_id: int | None = None,
        bedrooms: int | None = None,
        max_price: int | None = None,
        min_price: int | None = None,
        page: int = 1,
        apply_bedroom_filter: bool = False,
    ) -> ListingCollection:
        """Convenience method for executing rental searches with standard filters."""
        criteria = SearchCriteria.create_rental(
            city_id=city_id,
            property_type=property_type,
            neighborhood_id=neighborhood_id,
            bedrooms=bedrooms,
            max_price=max_price,
            min_price=min_price,
            page=page,
        )
        return self.search(criteria, apply_bedroom_filter=apply_bedroom_filter)

    def get_details(self, property_id: str) -> PropertyDetail:
        """Retrieve full details for a specific property by ID."""
        resp = self._gateway.fetch_detail(property_id)
        parser = self._parsers.detail_parser
        return parser.parse(resp.text, property_id=property_id, canonical_url=resp.final_url)

    def get_neighborhoods(
        self,
        city_id: int = int(CityId.TIMOTEO),
        transaction_type: int = 1,
        property_type: int = 0,
    ) -> NeighborhoodCatalog:
        """Retrieve dynamic neighborhood catalog for a city via AJAX endpoint."""
        resp = self._gateway.fetch_neighborhoods(city_id, transaction_type, property_type)
        parser = self._parsers.neighborhood_parser
        return parser.parse(resp.text)

    def get_cities(self) -> CityCatalog:
        """Retrieve catalog of municipalities supported by the portal."""
        resp = self._gateway.fetch_home()
        parser = self._parsers.city_parser
        return parser.parse(resp.text)

    def get_photos(self, property_id: str) -> PhotoGallery:
        """Retrieve photo gallery for a specific property."""
        detail = self.get_details(property_id)
        return detail.photos
