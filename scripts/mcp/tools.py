"""Model Context Protocol (MCP) tool adapters for Central Rental Research."""

from typing import Any
from vera_research.client import VeraRentalClient
from vera_research.domain.enums import CityId


class VeraMcpAdapter:
    """Adapts Vera Imobiliária rental client for consumption by MCP servers and tool registries."""

    def __init__(self, client: Any = None) -> None:
        """Initialize adapter with an abstract rental client."""
        self._client = client or VeraRentalClient()

    @classmethod
    def create_default(cls) -> "VeraMcpAdapter":
        """Factory constructor instantiating the default Vera provider."""
        return cls()

    def _resolve_city_id(self, city: str) -> int:
        """Resolve city name to Vera portal city ID."""
        name = city.lower().strip()
        if "fabriciano" in name:
            return int(CityId.FABRICIANO)
        if "ipatinga" in name:
            return int(CityId.IPATINGA)
        return int(CityId.TIMOTEO)

    def search_rentals(
        self,
        city: str = "Timóteo",
        min_price: float = 0.0,
        max_price: float = 0.0,
        bedrooms: int = 0,
        property_type: str = "",
        page: int = 1,
    ) -> dict[str, Any]:
        """Execute a rental property search for an MCP tool call."""
        cid = self._resolve_city_id(city)
        bed = bedrooms if bedrooms > 0 else None
        min_p = int(min_price) if min_price > 0 else None
        max_p = int(max_price) if max_price > 0 else None
        results = self._client.search_rentals(
            city_id=cid,
            bedrooms=bed,
            min_price=min_p,
            max_price=max_p,
            page=page,
        )
        return self._format_collection(results)

    def _format_collection(self, collection: Any) -> dict[str, Any]:
        """Format collection into standard dictionary."""
        return {
            "provider": "veraimobiliaria",
            "total_count": len(collection),
            "listings": [self._format_item(item) for item in collection],
        }

    def _format_item(self, item: Any) -> dict[str, Any]:
        """Format individual listing item."""
        ident = getattr(item, "identity", None)
        loc = getattr(item, "location", None)
        specs = getattr(item, "specs", None)
        return {
            "id": getattr(ident, "property_id", ""),
            "title": getattr(item, "title", ""),
            "price": getattr(item, "price_text", ""),
            "url": getattr(ident, "url", ""),
            "neighborhood": getattr(loc, "neighborhood", "") if loc else "",
            "city": getattr(loc, "city", "") if loc else "",
            "bedrooms": getattr(specs, "bedrooms", 0) if specs else 0,
            "bathrooms": getattr(specs, "bathrooms", 0) if specs else 0,
        }

    def get_property_detail(self, property_code: str) -> dict[str, Any]:
        """Retrieve complete property detail for an MCP tool call."""
        detail = self._client.get_details(property_code)
        ov = getattr(detail, "overview", None)
        loc = getattr(detail, "location", None)
        specs = getattr(detail, "specs", None)
        pricing = getattr(detail, "pricing", None)
        photos = getattr(detail, "photos", None)
        p_urls = getattr(photos, "photo_urls", []) if photos else []
        return {
            "id": getattr(ov, "property_id", str(property_code)),
            "title": getattr(ov, "title", ""),
            "description": getattr(detail, "description", ""),
            "price": getattr(pricing, "formatted_text", ""),
            "url": getattr(detail, "canonical_url", ""),
            "neighborhood": getattr(loc, "neighborhood", "") if loc else "",
            "city": getattr(loc, "city", "") if loc else "",
            "bedrooms": getattr(specs, "bedrooms", 0) if specs else 0,
            "bathrooms": getattr(specs, "bathrooms", 0) if specs else 0,
            "parking_spaces": getattr(specs, "parking_spaces", 0) if specs else 0,
            "area": getattr(specs, "usable_area", 0.0) if specs else 0.0,
            "photos": list(p_urls),
        }

    def get_facets(self) -> dict[str, Any]:
        """Retrieve available search facets for an MCP tool call."""
        cities = self._client.get_cities()
        c_list = [{"name": getattr(c, "name", "")} for c in getattr(cities, "cities", [])]
        return {"cities": c_list}

    def get_provider_info(self) -> dict[str, Any]:
        """Retrieve metadata about this rental provider adapter."""
        return {
            "provider_name": "veraimobiliaria",
            "coverage_region": "Timóteo, Coronel Fabriciano, Ipatinga",
            "supported_operations": ["search_rentals", "get_property_detail", "get_facets"],
        }
