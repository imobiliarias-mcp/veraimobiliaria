"""URL builder for veraimobiliaria.com.br search and detail routes."""

import re
from urllib.parse import unquote, urlencode, urljoin, urlsplit

from vera_research.domain.criteria import SearchCriteria


class VeraUrlBuilder:
    """Builds canonical URLs for property search, detail, and AJAX endpoints."""

    def __init__(self, base_url: str = "https://www.veraimobiliaria.com.br") -> None:
        """Initialize with a validated public portal origin."""
        parsed_url = urlsplit(base_url.strip())
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            raise ValueError("Public base URL must use HTTP(S) and include a host")
        if parsed_url.path not in {"", "/"} or parsed_url.query or parsed_url.fragment:
            raise ValueError("Public base URL must be an origin without path or query")
        self._base_url = base_url.rstrip("/")

    @property
    def base_url(self) -> str:
        """Return target base URL."""
        return self._base_url

    def build_search_url(self, criteria: SearchCriteria) -> str:
        """Construct full search URL with path segment and query string."""
        path_segment = criteria.page.to_path_segment()
        query = urlencode(criteria.query_parameters())
        return f"{self._base_url}/{path_segment}?{query}"

    def build_detail_url(self, property_id: str) -> str:
        """Construct direct property detail URL by numeric identifier."""
        clean_id = property_id.strip()
        return f"{self._base_url}/imovel/{clean_id}.html"

    def resolve_property_url(self, href: str, property_id: str) -> str:
        """Resolve a card link, or use the verified ID route when it is absent."""
        clean_id = property_id.strip()
        if not re.fullmatch(r"[0-9]+", clean_id) or int(clean_id) <= 0:
            raise ValueError(f"Invalid property ID for public URL: {property_id!r}")
        source_url = href.strip() if href.strip() else f"/imovel/{clean_id}.html"
        try:
            public_url, parsed_url, source_path = self._resolve_source_url(source_url)
        except ValueError as exc:
            raise ValueError(
                f"Invalid public property URL for listing {clean_id}: {href}"
            ) from exc
        has_dot_segments = self._has_dot_segments(source_path) or self._has_dot_segments(parsed_url.path)
        if has_dot_segments or not self._is_property_url(parsed_url, clean_id):
            raise ValueError(f"Invalid public property URL for listing {clean_id}: {href}")
        return public_url

    def _resolve_source_url(self, source_url: str):
        public_url = urljoin(f"{self._base_url}/", source_url)
        parsed_url = urlsplit(public_url)
        source_path = urlsplit(source_url).path
        return public_url, parsed_url, source_path

    def _has_dot_segments(self, path: str) -> bool:
        decoded_path = unquote(path)
        return any(segment in {".", ".."} for segment in decoded_path.split("/"))

    def _is_property_url(self, parsed_url, property_id: str) -> bool:
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            return False
        if parsed_url.netloc.lower() != urlsplit(self._base_url).netloc.lower():
            return False
        return parsed_url.path.startswith(f"/imovel/{property_id}/") or (
            parsed_url.path == f"/imovel/{property_id}.html"
        )

    def build_bairros_ajax_url(self) -> str:
        """Construct AJAX neighborhood dynamic lookup endpoint URL."""
        return f"{self._base_url}/asp/ajax/bairros2.asp"

    def resolve_photo_url(self, relative_path: str, high_res: bool = False) -> str:
        """Resolve full image URL, optionally swapping medium for high resolution."""
        path = relative_path.strip().lstrip("/")
        if high_res and "/m/" in path:
            path = path.replace("/m/", "/g/")
        return f"{self._base_url}/{path}"
