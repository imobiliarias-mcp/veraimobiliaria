"""HTML parser for property detail pages."""

import re
from bs4 import BeautifulSoup
from vera_research.domain.property import (
    PhotoGallery,
    PropertyDetail,
    PropertyLocation,
    PropertyOverview,
    PropertyPricing,
    PropertySpecs,
)
from vera_research.infrastructure.http_client import PropertyNotFoundError


class PropertyDetailParser:
    """Extracts property details from detail page markup."""

    def __init__(self, base_url: str = "https://www.veraimobiliaria.com.br") -> None:
        """Initialize parser with portal base URL."""
        self._base_url = base_url.rstrip("/")

    def parse(self, html: str, property_id: str, canonical_url: str = "") -> PropertyDetail:
        """Parse raw HTML and assemble PropertyDetail entity."""
        soup = BeautifulSoup(html, "html.parser")
        self._validate_content(soup, property_id)
        overview = self._parse_overview(soup, property_id)
        pricing = self._parse_pricing(soup)
        location = self._parse_location(soup)
        specs = self._parse_specs(soup)
        features = self._parse_features(soup)
        photos = self._extract_photos(soup)
        return PropertyDetail(
            overview=overview,
            pricing=pricing,
            location=location,
            specs=specs,
            features=features,
            photos=photos,
            canonical_url=canonical_url,
        )

    def _validate_content(self, soup: BeautifulSoup, property_id: str) -> None:
        """Validate that property detail markup is present."""
        node = soup.select_one("div.titulo, div#imovel h1, div#detalhes")
        if not node or not node.get_text(strip=True):
            raise PropertyNotFoundError(f"Property with ID '{property_id}' was not found.")

    def _parse_overview(self, soup: BeautifulSoup, property_id: str) -> PropertyOverview:
        """Extract title and textual description."""
        title_node = soup.select_one("div.titulo")
        title = title_node.get_text(" ", strip=True) if title_node else f"Imóvel {property_id}"
        desc = self._extract_description(soup)
        return PropertyOverview(property_id=property_id, title=title, description=desc)

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract description lines from details container."""
        cols = soup.select("div#detalhes .col-lg-4")
        if len(cols) >= 2:
            return cols[1].get_text("\n", strip=True)
        return ""

    def _parse_pricing(self, soup: BeautifulSoup) -> PropertyPricing:
        """Extract main price, IPTU, and condominium text."""
        h1 = soup.select_one("div.detalhes h1")
        price_text = h1.get_text(strip=True) if h1 else ""
        amount = self._parse_numeric_price(price_text)
        details_text = soup.select_one("div#detalhes").get_text("\n", strip=True) if soup.select_one("div#detalhes") else ""
        iptu = self._match_detail_field(details_text, r"IPTU[^\:]*:\s*([^\n\r]+)")
        condo = self._match_detail_field(details_text, r"Condom[íi]nio[^\:]*:\s*([^\n\r]+)")
        return PropertyPricing(amount=amount, formatted_text=price_text, iptu_text=iptu, condominio_text=condo)

    def _match_detail_field(self, text: str, pattern: str) -> str:
        """Extract named field from details text."""
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            return ""
        return match.group(1).strip()

    def _parse_numeric_price(self, text: str) -> float | None:
        """Convert 'R$ 2.500,00' into numeric float."""
        match = re.search(r"R\$\s*([\d\.,]+)", text)
        if not match:
            return None
        raw = match.group(1).replace(".", "").replace(",", ".")
        try:
            return float(raw)
        except ValueError:
            return None

    def _parse_location(self, soup: BeautifulSoup) -> PropertyLocation:
        """Extract address, neighborhood, city, and map link."""
        loc_node = soup.select_one("div.localizacao a")
        addr_text = loc_node.get_text(" ", strip=True) if loc_node else ""
        map_url = loc_node.get("href", "") if loc_node else ""
        parts = [p.strip() for p in addr_text.split(",")]
        neighborhood = ""
        city = "Timóteo"
        state = "MG"
        if len(parts) >= 3:
            loc_chunk = parts[2]
            if "-" in loc_chunk:
                sub = loc_chunk.split("-")
                neighborhood = sub[0].strip()
                city_chunk = sub[1].strip()
                if "/" in city_chunk:
                    city = city_chunk.split("/")[0].strip()
                    state = city_chunk.split("/")[1].strip()
        return PropertyLocation(address=addr_text, neighborhood=neighborhood, city=city, state=state, map_url=map_url)

    def _parse_specs(self, soup: BeautifulSoup) -> PropertySpecs:
        """Extract room counts and areas."""
        details_text = soup.select_one("div#detalhes").get_text("\n", strip=True) if soup.select_one("div#detalhes") else ""
        bedrooms = self._extract_counter(soup, "cama")
        bathrooms = self._extract_counter(soup, "chuveiro")
        parking = self._extract_counter(soup, "carro")
        built = self._match_detail_field(details_text, r"[ÁA]rea constru[íi]da:\s*([^\n\r]+)")
        lot = self._match_detail_field(details_text, r"[ÁA]rea do lote:\s*([^\n\r]+)")
        return PropertySpecs(bedrooms=bedrooms, bathrooms=bathrooms, parking_spaces=parking, built_area=built, lot_area=lot)

    def _extract_counter(self, soup: BeautifulSoup, icon_name: str) -> int:
        """Extract numeric spec next to icon."""
        img = soup.find("img", src=lambda s: s and icon_name in s)
        if not img or not img.parent:
            return 0
        span = img.parent.find("span")
        if not span:
            return 0
        match = re.search(r"(\d+)", span.get_text(strip=True))
        return int(match.group(1)) if match else 0

    def _parse_features(self, soup: BeautifulSoup) -> tuple[str, ...]:
        """Extract feature list."""
        cols = soup.select("div#detalhes .col-lg-4")
        if len(cols) < 2:
            return ()
        lines = [line.strip() for line in cols[1].get_text("\n").splitlines() if line.strip()]
        return tuple(lines)

    def _extract_photos(self, soup: BeautifulSoup) -> PhotoGallery:
        """Extract carousel photos and generate high-res counterparts."""
        carousel = soup.select_one("div#owl-carousel")
        if not carousel:
            return PhotoGallery()
        med_urls: list[str] = []
        high_urls: list[str] = []
        for img in carousel.find_all("img"):
            src = img.get("src", "").strip().lstrip("/")
            if not src:
                continue
            med_url = f"{self._base_url}/{src}"
            high_url = med_url.replace("/m/", "/g/")
            med_urls.append(med_url)
            high_urls.append(high_url)
        return PhotoGallery(photo_urls=tuple(dict.fromkeys(med_urls)), high_res_urls=tuple(dict.fromkeys(high_urls)))
