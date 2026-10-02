"""Unit tests for HTML parsers using fixture data."""

from dataclasses import replace

import pytest

from vera_research.infrastructure.http_client import PropertyNotFoundError
from vera_research.parsers.detail_parser import PropertyDetailParser
from vera_research.parsers.metadata_parser import CityParser, NeighborhoodParser
from vera_research.parsers.search_parser import SearchPageParser

SAMPLE_SEARCH_HTML = """
<main>
    <div class="row">
        <div class="col-lg-4">
            <div class="card">
                <a href="imovel/1197/galpao_cachoeira-do-vale_timoteo-mg.html">
                    <img class="card-img-top img-fluid" src="imagens/imovel/destaque/1197.png" />
                </a>
                <div class="card-body">
                    <div class="row">
                        <div class="col-lg-6">
                            <span class="preco">R$ 12.000,00</span><br>
                            <span class="endereco">Cachoeira do Vale, Timóteo/MG</span>
                        </div>
                        <div class="col-lg-6 icones">
                            <div class="col-4"><img src="./img/cama.png"><span>0</span></div>
                            <div class="col-4"><img src="./img/chuveiro.png"><span>0</span></div>
                            <div class="col-4"><img src="./img/carro.png"><span>0</span></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-lg-4">
            <div class="card">
                <a href="imovel/1151/casa_primavera_timoteo-mg.html">
                    <img class="card-img-top img-fluid" src="imagens/imovel/destaque/1151.png" />
                </a>
                <div class="card-body">
                    <div class="row">
                        <div class="col-lg-6">
                            <span class="preco">R$ 2.500,00</span><br>
                            <span class="endereco">Primavera, Timóteo/MG</span>
                        </div>
                        <div class="col-lg-6 icones">
                            <div class="col-4"><img src="./img/cama.png"><span>4</span></div>
                            <div class="col-4"><img src="./img/chuveiro.png"><span>2</span></div>
                            <div class="col-4"><img src="./img/carro.png"><span>1</span></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <nav aria-label="Page navigation" class="div-pagination">
        <ul class="pagination">
            <li class="active"><a href="imoveis/pagina_1.html#">1</a></li>
            <li><a href="imoveis/pagina_2.html">2</a></li>
        </ul>
    </nav>
</main>
"""

SAMPLE_DETAIL_HTML = """
<main>
    <div class="container-fluid" id="owl-carousel">
        <div class="owl-carousel owl-theme">
            <div class="item"><img src="imagens/imovel/1151/m/0005.jpeg" /></div>
            <div class="item"><img src="imagens/imovel/1151/m/0006.jpeg" /></div>
        </div>
    </div>
    <div class="container-fluid" id="imovel">
        <div class="col-12 titulo">CASA - <span class="span_aluguel">ALUGUEL</span> - Primavera, Timóteo/MG</div>
        <div class="col-12 localizacao">
            <a href="https://maps.google.com/?q=Primavera" target="_blank">Não infor., 0, Primavera - Timóteo/MG</a>
        </div>
        <div class="col-12 detalhes">
            <h1>R$ 2.500,00</h1>
            <div class="col-lg-4"><img src="./img/cama.png"><span>4 quartos</span></div>
            <div class="col-lg-4"><img src="./img/chuveiro.png"><span>2 banheiros</span></div>
            <div class="col-lg-4"><img src="./img/carro.png"><span>1 vagas</span></div>
        </div>
    </div>
    <div class="container-fluid" id="detalhes">
        <div class="row">
            <div class="col-lg-4">
                Código: 1151<br>
                Área construída: 180 m²<br>
                Área do lote: 360 m²<br>
                IPTU (mensal): R$ 80,00<br>
                Condomínio: Isento<br>
            </div>
            <div class="col-lg-4">
                4 quartos sendo 1 suíte<br>
                Sala ampla<br>
                Cozinha com armários<br>
            </div>
        </div>
    </div>
</main>
"""

SAMPLE_AJAX_BAIRROS = """
<option data-hidden="false" value="0">Bairro</option>
<option value="11" >Cachoeira+do+Vale</option>
<option value="37" >Centro+Sul</option>
<option value="77" >Primavera</option>
"""

SAMPLE_CIDADES_SELECT = """
<select name="txtcdcidadeBsc" id="div_cidade">
    <option value="0">CIDADE</option>
    <option value="1">Timóteo</option>
    <option value="2">Coronel Fabriciano</option>
    <option value="3">Ipatinga</option>
</select>
"""


def test_search_page_parser() -> None:
    """Validate parsing of search page HTML."""
    parser = SearchPageParser()
    collection = parser.parse(SAMPLE_SEARCH_HTML, page_number=1)
    assert len(collection) == 2
    assert collection.has_next_page is True
    assert collection.current_page == 1

    item1 = collection[0]
    assert item1.identity.property_id == "1197"
    assert item1.price_text == "R$ 12.000,00"
    assert item1.price_numeric == 12000.0
    assert item1.location.neighborhood == "Cachoeira do Vale"
    assert item1.location.city == "Timóteo"
    assert item1.specs.bedrooms == 0

    item2 = collection[1]
    assert item2.identity.property_id == "1151"
    assert item2.price_numeric == 2500.0
    assert item2.specs.bedrooms == 4
    assert item2.specs.bathrooms == 2
    assert item2.specs.parking_spaces == 1


def test_property_detail_parser() -> None:
    """Validate parsing of property detail HTML."""
    parser = PropertyDetailParser()
    detail = parser.parse(SAMPLE_DETAIL_HTML, property_id="1151", canonical_url="https://site.com/1151")

    assert detail.overview.property_id == "1151"
    assert "CASA" in detail.overview.title
    assert "4 quartos sendo 1 suíte" in detail.overview.description

    assert detail.pricing.amount == 2500.0
    assert detail.pricing.formatted_text == "R$ 2.500,00"
    assert detail.pricing.iptu_text == "R$ 80,00"
    assert detail.pricing.condominio_text == "Isento"

    assert detail.location.neighborhood == "Primavera"
    assert detail.location.city == "Timóteo"
    assert detail.specs.bedrooms == 4
    assert detail.specs.bathrooms == 2
    assert detail.specs.parking_spaces == 1
    assert detail.specs.built_area == "180 m²"
    assert detail.specs.lot_area == "360 m²"

    assert len(detail.photos) == 2
    assert detail.photos.first_photo() == "https://www.veraimobiliaria.com.br/imagens/imovel/1151/m/0005.jpeg"
    assert detail.photos.first_high_res_photo() == "https://www.veraimobiliaria.com.br/imagens/imovel/1151/g/0005.jpeg"


def test_property_detail_not_found_raises_exception() -> None:
    """Validate that missing/empty detail raises PropertyNotFoundError."""
    parser = PropertyDetailParser()
    with pytest.raises(PropertyNotFoundError):
        parser.parse("<html><body><div>Nenhum imovel encontrado</div></body></html>", property_id="99999")


def test_neighborhood_parser() -> None:
    """Validate parsing of dynamic bairros2.asp AJAX response."""
    parser = NeighborhoodParser()
    catalog = parser.parse(SAMPLE_AJAX_BAIRROS)
    assert len(catalog) == 3
    assert catalog[0].name == "Cachoeira do Vale"
    assert catalog[0].numeric_id == 11
    assert catalog[1].name == "Centro Sul"
    assert catalog[1].numeric_id == 37
    assert catalog[2].name == "Primavera"
    assert catalog[2].numeric_id == 77


def test_city_parser() -> None:
    """Validate parsing of city select options."""
    parser = CityParser()
    catalog = parser.parse(SAMPLE_CIDADES_SELECT)
    assert len(catalog) == 3
    assert catalog[0].name == "Timóteo"
    assert catalog[0].numeric_id == 1
    assert catalog[1].name == "Coronel Fabriciano"
    assert catalog[1].numeric_id == 2
    assert catalog[2].name == "Ipatinga"
    assert catalog[2].numeric_id == 3


@pytest.mark.parametrize(
    ("href", "expected_url"),
    [
        (
            "https://www.veraimobiliaria.com.br/imovel/1197/galpao.html",
            "https://www.veraimobiliaria.com.br/imovel/1197/galpao.html",
        ),
        (
            "//www.veraimobiliaria.com.br/imovel/1197/galpao.html",
            "https://www.veraimobiliaria.com.br/imovel/1197/galpao.html",
        ),
        (
            "/imovel/1197/galpao.html?id=1197&origem=busca",
            "https://www.veraimobiliaria.com.br/imovel/1197/galpao.html?id=1197&origem=busca",
        ),
    ],
)
def test_search_parser_resolves_urls_and_preserves_source_path(href, expected_url):
    source_link = "imovel/1197/galpao_cachoeira-do-vale_timoteo-mg.html"
    html = SAMPLE_SEARCH_HTML.replace(source_link, href, 1)
    listing = SearchPageParser().parse(html)[0]
    assert listing.identity.url_path == href
    assert listing.identity.url == expected_url


def test_search_parser_uses_configured_public_base_for_relative_url():
    source_link = "imovel/1197/galpao_cachoeira-do-vale_timoteo-mg.html"
    html = SAMPLE_SEARCH_HTML.replace(source_link, "imovel/1197/custom.html", 1)
    listing = SearchPageParser(public_base_url="https://public.example").parse(html)[0]
    assert listing.identity.url == "https://public.example/imovel/1197/custom.html"
    assert listing.identity.url_path == "imovel/1197/custom.html"


@pytest.mark.parametrize(
    "public_base_url",
    ["ftp://public.example", "https:///missing-host", "https://public.example/base"],
)
def test_search_parser_rejects_invalid_public_base(public_base_url):
    with pytest.raises(ValueError, match="[Pp]ublic base"):
        SearchPageParser(public_base_url=public_base_url)


def test_listing_collection_rejects_missing_or_relative_public_url():
    collection = SearchPageParser().parse(SAMPLE_SEARCH_HTML, page_number=1)
    listing = collection[0]

    invalid_public_urls = (
        "",
        "/imovel/1197/galpao.html",
        "https://www.veraimobiliaria.com.br/imovel/1197/../../search",
        "https://www.veraimobiliaria.com.br/imovel/1197/%2e%2e/search",
    )
    for public_url in invalid_public_urls:
        invalid_listing = replace(
            listing,
            identity=replace(listing.identity, url=public_url),
        )
        invalid_collection = replace(collection, items=(invalid_listing,))
        assert invalid_listing.identity.url_path == listing.identity.url_path
        with pytest.raises(ValueError, match="public property URL.*1197"):
            invalid_collection.to_dictionary()


def test_search_parser_wraps_malformed_authority_with_property_context():
    source_link = "imovel/1197/galpao_cachoeira-do-vale_timoteo-mg.html"
    html = SAMPLE_SEARCH_HTML.replace(source_link, "https://[::1", 1)
    with pytest.raises(ValueError, match="1197"):
        SearchPageParser().parse(html)


def test_search_parser_rejects_invalid_scheme_with_property_context():
    source_link = "imovel/1197/galpao_cachoeira-do-vale_timoteo-mg.html"
    html = SAMPLE_SEARCH_HTML.replace(source_link, "javascript:alert(1)", 1)
    with pytest.raises(ValueError, match="1197"):
        SearchPageParser().parse(html)


@pytest.mark.parametrize(
    "href",
    [
        "https://www.veraimobiliaria.com.br/imoveis/busca.html?txtcdcidadeBsc=1",
        "https://www.veraimobiliaria.com.br/asp/ajax/bairros2.asp",
        "imagens/imovel/destaque/1197.png",
    ],
)
def test_search_parser_rejects_non_property_destinations_with_context(href):
    source_link = "imovel/1197/galpao_cachoeira-do-vale_timoteo-mg.html"
    html = SAMPLE_SEARCH_HTML.replace(source_link, href, 1)
    with pytest.raises(ValueError, match="1197"):
        SearchPageParser().parse(html)


def test_url_builder_uses_documented_detail_route_only_with_valid_code():
    from vera_research.infrastructure.url_builder import VeraUrlBuilder

    builder = VeraUrlBuilder()
    assert builder.resolve_property_url("", "1197") == (
        "https://www.veraimobiliaria.com.br/imovel/1197.html"
    )
    with pytest.raises(ValueError):
        builder.resolve_property_url("", "")


def test_listing_collection_serializes_urls_and_preserves_native_metadata():
    collection = SearchPageParser().parse(SAMPLE_SEARCH_HTML, page_number=1)
    serialized = collection.to_dictionary()
    assert serialized["current_page"] == 1
    assert type(serialized["current_page"]) is int
    assert serialized["has_next_page"] is True
    assert type(serialized["has_next_page"]) is bool
    first_listing = serialized["listings"][0]
    assert first_listing["url_path"] == "imovel/1197/galpao_cachoeira-do-vale_timoteo-mg.html"
    assert first_listing["url"] == "https://www.veraimobiliaria.com.br/imovel/1197/galpao_cachoeira-do-vale_timoteo-mg.html"

    empty_result = SearchPageParser().parse("<html></html>", page_number=3).to_dictionary()
    assert empty_result["listings"] == []
    assert empty_result["current_page"] == 3
    assert empty_result["has_next_page"] is False
