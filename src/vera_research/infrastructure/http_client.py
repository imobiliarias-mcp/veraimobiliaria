"""HTTP client abstraction and Httpx implementation."""

from dataclasses import dataclass
from typing import Any, Protocol
import httpx


class PortalConnectionError(Exception):
    """Raised when portal network communication fails."""


class PropertyNotFoundError(Exception):
    """Raised when a requested property cannot be found or has no content."""


@dataclass(frozen=True)
class HttpResponse:
    """Encapsulates response data from HTTP operations."""

    status_code: int
    text: str
    final_url: str


class HttpClientProtocol(Protocol):
    """Contract for HTTP network operations."""

    def get(self, url: str, params: dict[str, Any] | None = None) -> HttpResponse:
        """Perform HTTP GET request."""
        ...

    def post(self, url: str, data: dict[str, Any] | None = None) -> HttpResponse:
        """Perform HTTP POST request."""
        ...


class HttpxHttpClient:
    """Concrete HTTP client using httpx with desktop User-Agent."""

    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    def __init__(self, timeout_seconds: float = 20.0) -> None:
        """Initialize HTTP client with timeout."""
        self._timeout = timeout_seconds
        self._headers = {"User-Agent": self.DEFAULT_USER_AGENT}

    def get(self, url: str, params: dict[str, Any] | None = None) -> HttpResponse:
        """Execute GET request with redirect following."""
        try:
            return self._execute_get(url, params)
        except httpx.HTTPError as error:
            raise PortalConnectionError(f"HTTP GET failed for {url}: {error}") from error

    def post(self, url: str, data: dict[str, Any] | None = None) -> HttpResponse:
        """Execute POST request with redirect following."""
        try:
            return self._execute_post(url, data)
        except httpx.HTTPError as error:
            raise PortalConnectionError(f"HTTP POST failed for {url}: {error}") from error

    def _execute_get(self, url: str, params: dict[str, Any] | None) -> HttpResponse:
        """Internal helper to dispatch GET request via httpx."""
        with httpx.Client(headers=self._headers, timeout=self._timeout, follow_redirects=True) as client:
            resp = client.get(url, params=params)
            text = self._decode_response(resp)
            return HttpResponse(status_code=resp.status_code, text=text, final_url=str(resp.url))

    def _execute_post(self, url: str, data: dict[str, Any] | None) -> HttpResponse:
        """Internal helper to dispatch POST request via httpx."""
        with httpx.Client(headers=self._headers, timeout=self._timeout, follow_redirects=True) as client:
            resp = client.post(url, data=data)
            text = self._decode_response(resp)
            return HttpResponse(status_code=resp.status_code, text=text, final_url=str(resp.url))

    def _decode_response(self, resp: httpx.Response) -> str:
        """Decode response body using Latin1/ISO-8859-1 or detected encoding."""
        try:
            return resp.content.decode("iso-8859-1")
        except UnicodeDecodeError:
            return resp.text
