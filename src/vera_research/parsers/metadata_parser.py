"""Parsers for cities and dynamic AJAX neighborhoods."""

from urllib.parse import unquote_plus
from bs4 import BeautifulSoup
from vera_research.domain.metadata import (
    City,
    CityCatalog,
    Neighborhood,
    NeighborhoodCatalog,
)


class NeighborhoodParser:
    """Parses dynamic HTML option markup from bairros2.asp AJAX endpoint."""

    def parse(self, html: str) -> NeighborhoodCatalog:
        """Transform raw <option> tags into NeighborhoodCatalog."""
        soup = BeautifulSoup(html, "html.parser")
        items: list[Neighborhood] = []
        for opt in soup.find_all("option"):
            raw_val = opt.get("value", "").strip()
            if not raw_val or raw_val == "0" or not raw_val.isdigit():
                continue
            raw_text = opt.get_text(strip=True)
            name = unquote_plus(raw_text).replace("+", " ").strip()
            items.append(Neighborhood(name=name, numeric_id=int(raw_val)))
        return NeighborhoodCatalog(items=tuple(items))


class CityParser:
    """Parses city select options from search page."""

    def parse(self, html: str) -> CityCatalog:
        """Transform city select options into CityCatalog."""
        soup = BeautifulSoup(html, "html.parser")
        select = soup.find("select", attrs={"name": "txtcdcidadeBsc"})
        if not select:
            return CityCatalog()
        cities: list[City] = []
        for opt in select.find_all("option"):
            raw_val = opt.get("value", "").strip()
            if not raw_val or raw_val == "0" or not raw_val.isdigit():
                continue
            name = opt.get_text(strip=True)
            cities.append(City(name=name, numeric_id=int(raw_val)))
        return CityCatalog(cities=tuple(cities))
