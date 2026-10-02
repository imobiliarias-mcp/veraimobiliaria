"""Unit tests for VeraRentalClient facade using stubbed network gateway."""

import pytest

from scripts import run_search as search_runner
from scripts.verify_research import run_target_search
from tests.test_parsers import (
    SAMPLE_AJAX_BAIRROS,
    SAMPLE_CIDADES_SELECT,
    SAMPLE_DETAIL_HTML,
    SAMPLE_SEARCH_HTML,
)
from vera_research.client import VeraRentalClient
from vera_research.collaborators import RentalNetworkGateway
from vera_research.domain.criteria import SearchCriteria
from vera_research.domain.enums import CityId
from vera_research.infrastructure.http_client import (
    HttpResponse,
    PropertyNotFoundError,
)
from vera_research.infrastructure.url_builder import VeraUrlBuilder
from vera_research.parsers.search_parser import SearchPageParser


class StubNetworkGateway:
    """Stub network gateway returning fixture data."""

    def __init__(self) -> None:
        """Initialize flags and stub responses."""
        self.last_criteria: SearchCriteria | None = None
        self.last_property_id: str | None = None
        self.last_city_id: int | None = None

    def fetch_search(self, criteria: SearchCriteria) -> HttpResponse:
        """Return stubbed search page response."""
        self.last_criteria = criteria
        return HttpResponse(status_code=200, text=SAMPLE_SEARCH_HTML, final_url="https://site.com/search")

    def fetch_detail(self, property_id: str) -> HttpResponse:
        """Return stubbed detail page response."""
        self.last_property_id = property_id
        if property_id == "99999":
            return HttpResponse(status_code=200, text="<html><body></body></html>", final_url="https://site.com/99999")
        return HttpResponse(status_code=200, text=SAMPLE_DETAIL_HTML, final_url=f"https://site.com/{property_id}")

    def fetch_neighborhoods(self, city_id: int, transaction_type: int = 1, property_type: int = 0) -> HttpResponse:
        """Return stubbed AJAX bairros response."""
        self.last_city_id = city_id
        return HttpResponse(status_code=200, text=SAMPLE_AJAX_BAIRROS, final_url="https://site.com/bairros")

    def fetch_home(self) -> HttpResponse:
        """Return stubbed cities select options."""
        return HttpResponse(status_code=200, text=SAMPLE_CIDADES_SELECT, final_url="https://site.com/")


def test_client_search_rentals() -> None:
    """Validate client search_rentals facade dispatch and parsing."""
    gateway = StubNetworkGateway()
    client = VeraRentalClient(gateway=gateway)

    results = client.search_rentals(city_id=1, bedrooms=2, max_price=5000)
    assert len(results) == 2
    assert gateway.last_criteria is not None
    assert gateway.last_criteria.location.city_id == 1
    assert gateway.last_criteria.bedrooms.count == 2
    assert gateway.last_criteria.price_range.maximum == 5000


def test_client_search_with_bedroom_filtering() -> None:
    """Validate client-side bedroom filtering for strict matching."""
    gateway = StubNetworkGateway()
    client = VeraRentalClient(gateway=gateway)

    results = client.search_rentals(city_id=1, bedrooms=4, apply_bedroom_filter=True)
    # SAMPLE_SEARCH_HTML has one 0-bed (1197) and one 4-bed (1151)
    assert len(results) == 1
    assert results[0].identity.property_id == "1151"


def test_client_get_details() -> None:
    """Validate client get_details retrieval and parsing."""
    gateway = StubNetworkGateway()
    client = VeraRentalClient(gateway=gateway)

    detail = client.get_details("1151")
    assert detail.overview.property_id == "1151"
    assert detail.pricing.amount == 2500.0
    assert len(detail.photos) == 2


def test_client_get_details_not_found() -> None:
    """Validate that not found property raises PropertyNotFoundError."""
    gateway = StubNetworkGateway()
    client = VeraRentalClient(gateway=gateway)

    with pytest.raises(PropertyNotFoundError):
        client.get_details("99999")


def test_client_get_neighborhoods() -> None:
    """Validate dynamic AJAX neighborhood lookup via client."""
    gateway = StubNetworkGateway()
    client = VeraRentalClient(gateway=gateway)

    bairros = client.get_neighborhoods(city_id=int(CityId.TIMOTEO))
    assert len(bairros) == 3
    assert bairros.find_by_name("Primavera") is not None


def test_client_get_cities() -> None:
    """Validate cities catalog discovery via client."""
    gateway = StubNetworkGateway()
    client = VeraRentalClient(gateway=gateway)

    cities = client.get_cities()
    assert len(cities) == 3
    assert cities.find_by_name("Timóteo") is not None


class StubHttpClient:
    """Capture one search request while returning the HTML fixture."""

    def __init__(self) -> None:
        self.requested_urls: list[str] = []

    def get(self, url: str, params=None) -> HttpResponse:
        self.requested_urls.append(url)
        return HttpResponse(status_code=200, text=SAMPLE_SEARCH_HTML, final_url=url)

    def post(self, url: str, data=None) -> HttpResponse:
        self.requested_urls.append(url)
        return HttpResponse(status_code=200, text="", final_url=url)


def test_client_forwards_custom_public_base_and_does_not_fetch_details() -> None:
    http_client = StubHttpClient()
    gateway = RentalNetworkGateway(
        http_client=http_client,
        url_builder=VeraUrlBuilder(base_url="https://public.example"),
    )
    client = VeraRentalClient(gateway=gateway)

    result = client.search_rentals()
    listing = result.to_dictionary()["listings"][0]
    assert listing["url"] == "https://public.example/imovel/1197/galpao_cachoeira-do-vale_timoteo-mg.html"
    assert listing["url_path"] == "imovel/1197/galpao_cachoeira-do-vale_timoteo-mg.html"
    assert len(http_client.requested_urls) == 1
    assert http_client.requested_urls[0].startswith("https://public.example/imoveis/")


def test_search_cli_prints_public_link(monkeypatch, capsys) -> None:
    class StubClient:
        def search_rentals(self, **kwargs):
            return SearchPageParser().parse(SAMPLE_SEARCH_HTML)

    monkeypatch.setattr(search_runner, "VeraRentalClient", lambda: StubClient())
    monkeypatch.setattr("sys.argv", ["run_search.py"])
    search_runner.main()
    assert "Link: https://www.veraimobiliaria.com.br/imovel/1197/galpao_cachoeira-do-vale_timoteo-mg.html" in capsys.readouterr().out


def test_verification_runner_prints_public_link(capsys) -> None:
    class StubClient:
        def search(self, criteria):
            from vera_research.parsers.search_parser import SearchPageParser

            return SearchPageParser().parse(SAMPLE_SEARCH_HTML)

    run_target_search(StubClient())
    assert "Link: https://www.veraimobiliaria.com.br/imovel/1197/galpao_cachoeira-do-vale_timoteo-mg.html" in capsys.readouterr().out
