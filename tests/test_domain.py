"""Unit tests for domain models, value objects, and first-class collections."""

import pytest
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
from vera_research.domain.property import PhotoGallery
from vera_research.domain.values import PageNumber, PriceRange, RoomCount


def test_price_range_formatting() -> None:
    """Validate price range string formats for faixavalor."""
    assert PriceRange().to_faixavalor_code() == "0"
    assert PriceRange(minimum=1000, maximum=3000).to_faixavalor_code() == "1000a3000"
    assert PriceRange(maximum=2000).to_faixavalor_code() == "0a2000"
    assert PriceRange(minimum=1500).to_faixavalor_code() == "1500a100000000000"


def test_price_range_negative_raises_error() -> None:
    """Verify negative prices raise ValueError."""
    with pytest.raises(ValueError):
        PriceRange(minimum=-500)
    with pytest.raises(ValueError):
        PriceRange(maximum=-100)


def test_room_count_behavior() -> None:
    """Verify room count constraints and validation."""
    rc = RoomCount(2)
    assert rc.to_param_code() == "2"
    with pytest.raises(ValueError):
        RoomCount(-1)


def test_page_number_path_and_validation() -> None:
    """Verify page number path segments and boundary validation."""
    assert PageNumber(1).to_path_segment() == "imoveis/busca.html"
    assert PageNumber(2).to_path_segment() == "imoveis/pagina_2.html"
    with pytest.raises(ValueError):
        PageNumber(0)


def test_search_criteria_target_query_parameters() -> None:
    """Validate query parameters matching target prompt."""
    criteria = SearchCriteria(
        scope=SearchScope(TransactionType.ALUGUEL, PropertyType.TODOS),
        location=LocationCriteria(city_id=1),
        price_range=PriceRange(),
        bedrooms=RoomCount(2),
        page=PageNumber(1),
    )
    params = criteria.query_parameters()
    assert params["txtcdtpnegocioBsc"] == "1"
    assert params["txtcdtpimovelBsc"] == "0"
    assert params["txtcdcidadeBsc"] == "1"
    assert params["faixavalor"] == "0"
    assert params["quartos"] == "2"
    assert params["singlebutton"] == ""


def test_search_criteria_with_neighborhood() -> None:
    """Validate neighborhood query parameter inclusion."""
    criteria = SearchCriteria.create_rental(
        city_id=1,
        neighborhood_id=11,
        bedrooms=3,
        min_price=1000,
        max_price=3000,
    )
    params = criteria.query_parameters()
    assert params["txtcdbairrocidadeBsc"] == "11"
    assert params["quartos"] == "3"
    assert params["faixavalor"] == "1000a3000"


def test_listing_collection_filtering_and_iteration() -> None:
    """Verify ListingCollection behaves as a first-class collection."""
    l1 = ListingSummary(
        identity=ListingIdentity("1", "imovel/1.html"),
        title="Imóvel 1",
        location=ListingLocation("Bairro A", "Timóteo"),
        price_text="R$ 1.500,00",
        price_numeric=1500.0,
        specs=ListingSpecs(bedrooms=2, bathrooms=1, parking_spaces=1),
    )
    l2 = ListingSummary(
        identity=ListingIdentity("2", "imovel/2.html"),
        title="Imóvel 2",
        location=ListingLocation("Bairro B", "Timóteo"),
        price_text="R$ 2.500,00",
        price_numeric=2500.0,
        specs=ListingSpecs(bedrooms=4, bathrooms=2, parking_spaces=2),
    )
    col = ListingCollection(items=(l1, l2), current_page=1, has_next_page=False)
    assert len(col) == 2
    assert not col.is_empty()
    assert col[0] == l1

    # Filter exact bedrooms
    filtered_exact = col.filter_by_bedrooms(2)
    assert len(filtered_exact) == 1
    assert filtered_exact[0].identity.property_id == "1"

    # Filter min bedrooms
    filtered_min = col.filter_by_min_bedrooms(3)
    assert len(filtered_min) == 1
    assert filtered_min[0].identity.property_id == "2"


def test_photo_gallery_collection() -> None:
    """Verify PhotoGallery methods."""
    med = ("https://site.com/m/01.jpg", "https://site.com/m/02.jpg")
    high = ("https://site.com/g/01.jpg", "https://site.com/g/02.jpg")
    gallery = PhotoGallery(photo_urls=med, high_res_urls=high)
    assert len(gallery) == 2
    assert gallery.first_photo() == "https://site.com/m/01.jpg"
    assert gallery.first_high_res_photo() == "https://site.com/g/01.jpg"


def test_location_catalogs() -> None:
    """Verify CityCatalog and NeighborhoodCatalog lookups."""
    n1 = Neighborhood(name="Centro Sul", numeric_id=37)
    n2 = Neighborhood(name="Primavera", numeric_id=77)
    nc = NeighborhoodCatalog(items=(n1, n2))
    assert len(nc) == 2
    assert nc.find_by_id(37) == n1
    assert nc.find_by_name("primavera") == n2
    assert nc.find_by_id(999) is None

    c1 = City(name="Timóteo", numeric_id=1, neighborhoods=nc)
    cc = CityCatalog(cities=(c1,))
    assert len(cc) == 1
    assert cc.find_by_id(1) == c1
    assert cc.find_by_name("timóteo") == c1
    assert cc.find_by_name("ipatinga") is None
