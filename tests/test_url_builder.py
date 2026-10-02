"""Unit tests for VeraUrlBuilder constructing portal URLs."""

from urllib.parse import parse_qs, urlparse
from vera_research.domain.criteria import (
    LocationCriteria,
    SearchCriteria,
    SearchScope,
)
from vera_research.domain.enums import PropertyType, TransactionType
from vera_research.domain.values import PageNumber, PriceRange, RoomCount
from vera_research.infrastructure.url_builder import VeraUrlBuilder


def test_target_url_reproduction() -> None:
    """Validate construction of the exact target search URL from the prompt."""
    builder = VeraUrlBuilder()
    criteria = SearchCriteria(
        scope=SearchScope(TransactionType.ALUGUEL, PropertyType.TODOS),
        location=LocationCriteria(city_id=1),
        price_range=PriceRange(),
        bedrooms=RoomCount(2),
        page=PageNumber(1),
    )
    url = builder.build_search_url(criteria)
    parsed = urlparse(url)
    assert parsed.scheme == "https"
    assert parsed.netloc == "www.veraimobiliaria.com.br"
    assert parsed.path == "/imoveis/busca.html"

    params = parse_qs(parsed.query, keep_blank_values=True)
    assert params["txtcdtpnegocioBsc"] == ["1"]
    assert params["txtcdtpimovelBsc"] == ["0"]
    assert params["txtcdcidadeBsc"] == ["1"]
    assert params["faixavalor"] == ["0"]
    assert params["quartos"] == ["2"]
    assert params["singlebutton"] == [""]


def test_pagination_url_path() -> None:
    """Validate that page 2 constructs /imoveis/pagina_2.html."""
    builder = VeraUrlBuilder()
    criteria = SearchCriteria.create_rental(city_id=1, page=2)
    url = builder.build_search_url(criteria)
    parsed = urlparse(url)
    assert parsed.path == "/imoveis/pagina_2.html"


def test_property_detail_url() -> None:
    """Validate property detail URL generation."""
    builder = VeraUrlBuilder()
    url = builder.build_detail_url("1197")
    assert url == "https://www.veraimobiliaria.com.br/imovel/1197.html"


def test_ajax_bairros_url() -> None:
    """Validate AJAX dynamic neighborhoods URL generation."""
    builder = VeraUrlBuilder()
    url = builder.build_bairros_ajax_url()
    assert url == "https://www.veraimobiliaria.com.br/asp/ajax/bairros2.asp"


def test_photo_url_resolution() -> None:
    """Validate relative photo resolution and high-res /g/ conversion."""
    builder = VeraUrlBuilder()
    rel = "imagens/imovel/1151/m/0005.jpeg"
    med = builder.resolve_photo_url(rel, high_res=False)
    high = builder.resolve_photo_url(rel, high_res=True)

    assert med == "https://www.veraimobiliaria.com.br/imagens/imovel/1151/m/0005.jpeg"
    assert high == "https://www.veraimobiliaria.com.br/imagens/imovel/1151/g/0005.jpeg"
