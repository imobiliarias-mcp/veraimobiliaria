"""Live integration tests against veraimobiliaria.com.br."""

import pytest
from vera_research.client import VeraRentalClient
from vera_research.domain.criteria import (
    LocationCriteria,
    SearchCriteria,
    SearchScope,
)
from vera_research.domain.enums import CityId, PropertyType, TransactionType
from vera_research.domain.values import PageNumber, PriceRange, RoomCount


@pytest.fixture(scope="module")
def client() -> VeraRentalClient:
    """Fixture providing initialized client."""
    return VeraRentalClient()


def test_live_target_prompt_url_search(client: VeraRentalClient) -> None:
    """Reproduce the target search query from the prompt against live site."""
    criteria = SearchCriteria(
        scope=SearchScope(TransactionType.ALUGUEL, PropertyType.TODOS),
        location=LocationCriteria(city_id=1),
        price_range=PriceRange(),
        bedrooms=RoomCount(2),
        page=PageNumber(1),
    )
    results = client.search(criteria)
    assert len(results) >= 1
    for item in results:
        assert item.identity.property_id
        assert item.location.city.lower() == "timóteo"


def test_live_rental_search(client: VeraRentalClient) -> None:
    """Verify live rental search in Timóteo."""
    rentals = client.search_rentals(city_id=int(CityId.TIMOTEO))
    assert len(rentals) >= 1
    # Check that prices and locations are populated
    for r in rentals:
        assert r.price_text
        assert r.location.neighborhood


def test_live_property_detail_retrieval(client: VeraRentalClient) -> None:
    """Verify live property detail retrieval for known rental property 1151."""
    detail = client.get_details("1151")
    assert detail.overview.property_id == "1151"
    assert "CASA" in detail.overview.title
    assert detail.pricing.amount == 2500.0
    assert detail.location.neighborhood == "Primavera"
    assert detail.specs.bedrooms == 4
    assert len(detail.photos) >= 5
    assert detail.photos.first_photo().startswith("https://www.veraimobiliaria.com.br/imagens/imovel/1151/m/")
    assert detail.photos.first_high_res_photo().startswith("https://www.veraimobiliaria.com.br/imagens/imovel/1151/g/")


def test_live_dynamic_neighborhoods_ajax(client: VeraRentalClient) -> None:
    """Verify dynamic AJAX neighborhood discovery for Timóteo rentals."""
    bairros = client.get_neighborhoods(
        city_id=int(CityId.TIMOTEO),
        transaction_type=int(TransactionType.ALUGUEL),
        property_type=int(PropertyType.TODOS),
    )
    assert len(bairros) >= 3
    # Check that known neighborhoods exist in the dynamic catalog
    names = [b.name for b in bairros]
    assert any("Primavera" in n for n in names)
    assert any("Cachoeira do Vale" in n for n in names)
