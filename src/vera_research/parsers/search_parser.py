"""HTML parser for search results page."""

import re

from bs4 import BeautifulSoup, Tag

from vera_research.domain.listing import (
    ListingCollection,
    ListingIdentity,
    ListingLocation,
    ListingSpecs,
    ListingSummary,
)
from vera_research.infrastructure.url_builder import VeraUrlBuilder


class SearchPageParser:
    """Transforms raw search result HTML into domain ListingCollection."""

    def __init__(self, public_base_url: str = "https://www.veraimobiliaria.com.br") -> None:
        """Initialize the parser with the canonical public portal base."""
        self._url_builder = VeraUrlBuilder(public_base_url)

    def parse(self, html: str, page_number: int = 1) -> ListingCollection:
        """Parse raw HTML and construct the first-class listing collection."""
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.find_all("div", class_="card")
        items = tuple(self._parse_card(card) for card in cards if card.find("a"))
        has_next = self._detect_next_page(soup, page_number)
        return ListingCollection(items=items, current_page=page_number, has_next_page=has_next)

    def _parse_card(self, card: Tag) -> ListingSummary:
        """Transform a single .card tag into a ListingSummary."""
        link_node = card.find("a")
        link = link_node.get("href", "") if link_node else ""
        prop_id = self._extract_card_property_id(card, link)
        public_url = self._url_builder.resolve_property_url(link, prop_id)
        thumb = self._extract_thumbnail(card)
        location = self._parse_location(card)
        price_text = self._parse_price(card)
        price_num = self._parse_numeric_price(price_text)
        specs = self._parse_specs(card)
        title = self._derive_title(link, location)
        return ListingSummary(
            identity=ListingIdentity(property_id=prop_id, url_path=link, url=public_url),
            title=title,
            location=location,
            price_text=price_text,
            price_numeric=price_num,
            specs=specs,
            thumbnail_url=thumb,
        )

    def _extract_property_id(self, link: str) -> str:
        """Extract numeric property ID from URL link."""
        match = re.search(r"imovel/(\d+)", link)
        if not match:
            return ""
        return match.group(1)

    def _extract_card_property_id(self, card: Tag, primary_link: str) -> str:
        property_id = self._extract_property_id(primary_link)
        if property_id:
            return property_id
        for link_node in card.find_all("a", href=True):
            property_id = self._extract_property_id(link_node.get("href", ""))
            if property_id:
                return property_id
        return self._extract_thumbnail_property_id(card)

    def _extract_thumbnail_property_id(self, card: Tag) -> str:
        thumbnail = self._extract_thumbnail(card)
        if thumbnail is None:
            return ""
        match = re.search(r"(?:imovel|destaque)/(\d+)", thumbnail)
        if not match:
            return ""
        return match.group(1)

    def _extract_thumbnail(self, card: Tag) -> str | None:
        """Extract card thumbnail image source."""
        img = card.find("img", class_="card-img-top")
        if not img:
            return None
        return img.get("src")

    def _parse_location(self, card: Tag) -> ListingLocation:
        """Extract neighborhood, city, and state from card."""
        node = card.find("span", class_="endereco")
        if not node:
            return ListingLocation(neighborhood="", city="")
        text = node.get_text(strip=True)
        return self._split_location_text(text)

    def _split_location_text(self, text: str) -> ListingLocation:
        """Split 'Bairro, Cidade/UF' text."""
        parts = [p.strip() for p in text.split(",")]
        neighborhood = parts[0] if parts else ""
        if len(parts) < 2:
            return ListingLocation(neighborhood=neighborhood, city="")
        subparts = [p.strip() for p in parts[1].split("/")]
        city = subparts[0] if subparts else ""
        state = subparts[1] if len(subparts) > 1 else "MG"
        return ListingLocation(neighborhood=neighborhood, city=city, state=state)

    def _parse_price(self, card: Tag) -> str:
        """Extract formatted price text from card."""
        node = card.find("span", class_="preco")
        if not node:
            return "Preço a consultar"
        return node.get_text(strip=True)

    def _parse_numeric_price(self, price_text: str) -> float | None:
        """Convert 'R$ 1.500,00' into numeric float."""
        match = re.search(r"R\$\s*([\d\.,]+)", price_text)
        if not match:
            return None
        raw = match.group(1).replace(".", "").replace(",", ".")
        try:
            return float(raw)
        except ValueError:
            return None

    def _parse_specs(self, card: Tag) -> ListingSpecs:
        """Extract bedroom, bathroom, and garage counts."""
        bedrooms = self._extract_icon_counter(card, "cama")
        bathrooms = self._extract_icon_counter(card, "chuveiro")
        parking = self._extract_icon_counter(card, "carro")
        return ListingSpecs(bedrooms=bedrooms, bathrooms=bathrooms, parking_spaces=parking)

    def _extract_icon_counter(self, card: Tag, icon_keyword: str) -> int:
        """Extract integer counter next to spec icon."""
        img = card.find("img", src=lambda s: s and icon_keyword in s)
        if not img or not img.parent:
            return 0
        span = img.parent.find("span")
        if not span:
            return 0
        text = span.get_text(strip=True)
        return int(text) if text.isdigit() else 0

    def _derive_title(self, link: str, location: ListingLocation) -> str:
        """Generate readable listing title."""
        match = re.search(r"imovel/\d+/([^\.]+)\.html", link)
        if not match:
            return f"Imóvel em {location.neighborhood}, {location.city}"
        slug = match.group(1).replace("_", " - ").replace("-", " ")
        return slug.title()

    def _detect_next_page(self, soup: BeautifulSoup, current_page: int) -> bool:
        """Check if next page navigation is available."""
        nav = soup.find("nav", class_="div-pagination")
        if not nav:
            return False
        next_link = nav.find("a", href=lambda h: h and f"pagina_{current_page + 1}" in h)
        return next_link is not None
