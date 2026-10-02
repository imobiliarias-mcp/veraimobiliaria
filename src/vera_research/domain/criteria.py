"""Search criteria and specification models for Vera Imobiliária."""

from dataclasses import dataclass, field
from vera_research.domain.enums import CityId, PropertyType, TransactionType
from vera_research.domain.values import PageNumber, PriceRange, RoomCount


@dataclass(frozen=True)
class LocationCriteria:
    """Location parameters: municipality and optional neighborhood ID."""

    city_id: int = int(CityId.TIMOTEO)
    neighborhood_id: int | None = None

    def query_parameters(self) -> dict[str, str]:
        """Convert location criteria into URL query parameters."""
        params = {"txtcdcidadeBsc": str(self.city_id)}
        if self.neighborhood_id is not None:
            params["txtcdbairrocidadeBsc"] = str(self.neighborhood_id)
        return params


@dataclass(frozen=True)
class SearchScope:
    """Defines transaction type and property category."""

    transaction: TransactionType = TransactionType.ALUGUEL
    property_type: PropertyType = PropertyType.TODOS

    def query_parameters(self) -> dict[str, str]:
        """Convert scope into URL query parameters."""
        return {
            "txtcdtpnegocioBsc": str(int(self.transaction)),
            "txtcdtpimovelBsc": str(int(self.property_type)),
        }


@dataclass(frozen=True)
class SearchCriteria:
    """Top-level search criteria container."""

    scope: SearchScope = field(default_factory=SearchScope)
    location: LocationCriteria = field(default_factory=LocationCriteria)
    price_range: PriceRange = field(default_factory=PriceRange)
    bedrooms: RoomCount = field(default_factory=RoomCount)
    page: PageNumber = field(default_factory=PageNumber)

    def query_parameters(self) -> dict[str, str]:
        """Combine all search criteria into query parameters dictionary."""
        params: dict[str, str] = {}
        params.update(self.scope.query_parameters())
        params.update(self.location.query_parameters())
        params["faixavalor"] = self.price_range.to_faixavalor_code()
        params["quartos"] = self.bedrooms.to_param_code()
        params["singlebutton"] = ""
        return params

    @classmethod
    def create_rental(
        cls,
        city_id: int = int(CityId.TIMOTEO),
        property_type: PropertyType = PropertyType.TODOS,
        neighborhood_id: int | None = None,
        bedrooms: int | None = None,
        max_price: int | None = None,
        min_price: int | None = None,
        page: int = 1,
    ) -> "SearchCriteria":
        """Factory helper to construct rental search criteria quickly."""
        room_count = RoomCount(bedrooms) if bedrooms is not None else RoomCount(0)
        price_range = PriceRange(minimum=min_price, maximum=max_price)
        return cls(
            scope=SearchScope(TransactionType.ALUGUEL, property_type),
            location=LocationCriteria(city_id=city_id, neighborhood_id=neighborhood_id),
            price_range=price_range,
            bedrooms=room_count,
            page=PageNumber(value=page),
        )
