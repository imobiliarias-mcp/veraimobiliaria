"""Network gateway and parser suite collaborators for rental research client."""

from vera_research.domain.criteria import SearchCriteria
from vera_research.infrastructure.http_client import (
    HttpClientProtocol,
    HttpResponse,
    HttpxHttpClient,
)
from vera_research.infrastructure.url_builder import VeraUrlBuilder
from vera_research.parsers.detail_parser import PropertyDetailParser
from vera_research.parsers.metadata_parser import CityParser, NeighborhoodParser
from vera_research.parsers.search_parser import SearchPageParser


class RentalNetworkGateway:
    """Dispatches HTTP requests for rental searches, details, and dynamic metadata."""

    def __init__(
        self,
        http_client: HttpClientProtocol | None = None,
        url_builder: VeraUrlBuilder | None = None,
    ) -> None:
        """Initialize gateway with network client and URL builder."""
        self._http = http_client or HttpxHttpClient()
        self._builder = url_builder or VeraUrlBuilder()

    def public_base_url(self) -> str:
        """Expose the canonical public base for result-link normalization."""
        return self._builder.base_url

    def fetch_search(self, criteria: SearchCriteria) -> HttpResponse:
        """Fetch search results page for given criteria."""
        url = self._builder.build_search_url(criteria)
        return self._http.get(url)

    def fetch_detail(self, property_id: str) -> HttpResponse:
        """Fetch detail page for a given property ID."""
        url = self._builder.build_detail_url(property_id)
        return self._http.get(url)

    def fetch_neighborhoods(
        self,
        city_id: int,
        transaction_type: int = 1,
        property_type: int = 0,
    ) -> HttpResponse:
        """Query dynamic AJAX endpoint for neighborhoods."""
        url = self._builder.build_bairros_ajax_url()
        data = {
            "cidade": str(city_id),
            "tpnegocio": str(transaction_type),
            "tpimovel": str(property_type),
            "tabindex": "18",
        }
        return self._http.post(url, data=data)

    def fetch_home(self) -> HttpResponse:
        """Fetch search form to discover portal cities."""
        criteria = SearchCriteria()
        url = self._builder.build_search_url(criteria)
        return self._http.get(url)


class ListingParserBundle:
    """Aggregates search and city parsers."""

    def __init__(
        self,
        search_parser: SearchPageParser | None = None,
        city_parser: CityParser | None = None,
    ) -> None:
        """Initialize search and city parsers."""
        self._search = search_parser or SearchPageParser()
        self._city = city_parser or CityParser()

    @property
    def search_parser(self) -> SearchPageParser:
        """Return search parser."""
        return self._search

    @property
    def city_parser(self) -> CityParser:
        """Return city parser."""
        return self._city


class DetailParserBundle:
    """Aggregates detail view and dynamic neighborhood parsers."""

    def __init__(
        self,
        detail_parser: PropertyDetailParser | None = None,
        neighborhood_parser: NeighborhoodParser | None = None,
    ) -> None:
        """Initialize detail and neighborhood parsers."""
        self._detail = detail_parser or PropertyDetailParser()
        self._neighborhood = neighborhood_parser or NeighborhoodParser()

    @property
    def detail_parser(self) -> PropertyDetailParser:
        """Return detail parser."""
        return self._detail

    @property
    def neighborhood_parser(self) -> NeighborhoodParser:
        """Return neighborhood parser."""
        return self._neighborhood


class RentalParserSuite:
    """Composite suite containing listing and detail parser bundles."""

    def __init__(
        self,
        listing_bundle: ListingParserBundle | None = None,
        detail_bundle: DetailParserBundle | None = None,
        public_base_url: str | None = None,
    ) -> None:
        """Initialize suite with listing and detail bundles."""
        self._listing = listing_bundle or self._build_listing_bundle(public_base_url)
        self._detail = detail_bundle or DetailParserBundle()

    def _build_listing_bundle(self, public_base_url: str | None) -> ListingParserBundle:
        if public_base_url is None:
            return ListingParserBundle()
        search_parser = SearchPageParser(public_base_url=public_base_url)
        return ListingParserBundle(search_parser=search_parser)

    @property
    def search_parser(self) -> SearchPageParser:
        """Return search parser collaborator."""
        return self._listing.search_parser

    @property
    def city_parser(self) -> CityParser:
        """Return city parser collaborator."""
        return self._listing.city_parser

    @property
    def detail_parser(self) -> PropertyDetailParser:
        """Return detail parser collaborator."""
        return self._detail.detail_parser

    @property
    def neighborhood_parser(self) -> NeighborhoodParser:
        """Return neighborhood parser collaborator."""
        return self._detail.neighborhood_parser
