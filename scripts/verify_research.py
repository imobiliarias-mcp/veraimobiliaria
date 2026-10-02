#!/usr/bin/env python3
"""Verification runner demonstrating reverse-engineered endpoints and MCP client."""

import sys
from pathlib import Path

# Ensure src is in python path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from vera_research import (
    CityId,
    LocationCriteria,
    PriceRange,
    PropertyType,
    RoomCount,
    SearchCriteria,
    SearchScope,
    TransactionType,
    VeraRentalClient,
)


def run_target_search(client: VeraRentalClient) -> None:
    """Execute reproduction of user prompt target search."""
    print("--- 1. Target URL Search (Aluguel / 2 quartos / Timóteo) ---")
    criteria = SearchCriteria(
        scope=SearchScope(TransactionType.ALUGUEL, PropertyType.TODOS),
        location=LocationCriteria(city_id=1),
        price_range=PriceRange(),
        bedrooms=RoomCount(2),
    )
    results = client.search(criteria)
    print(f"Total matching listings: {len(results)}")
    for item in results:
        print(f"  [{item.identity.property_id}] {item.title[:45]} | {item.price_text} | {item.location.neighborhood} ({item.specs.bedrooms} quartos)")
        print(f"    Link: {item.identity.url}")


def run_rental_search(client: VeraRentalClient) -> None:
    """Execute standard rental search in Timóteo."""
    print("\n--- 2. Timóteo Rental Listings Search ---")
    results = client.search_rentals(city_id=int(CityId.TIMOTEO))
    print(f"Total rental listings: {len(results)}")
    for item in results:
        print(f"  [{item.identity.property_id}] {item.title[:45]} | {item.price_text} | {item.location.neighborhood}")


def run_detail_retrieval(client: VeraRentalClient) -> None:
    """Retrieve details for sample rental property (1151)."""
    print("\n--- 3. Property Detail Retrieval (House 1151) ---")
    detail = client.get_details("1151")
    print(f"Title: {detail.overview.title}")
    print(f"Price: R$ {detail.pricing.amount:,.2f}" if detail.pricing.amount else f"Price: {detail.pricing.formatted_text}")
    print(f"IPTU: {detail.pricing.iptu_text} | Condomínio: {detail.pricing.condominio_text}")
    print(f"Location: {detail.location.neighborhood}, {detail.location.city} - {detail.location.state}")
    print(f"Rooms: {detail.specs.bedrooms} dorms, {detail.specs.bathrooms} banheiros, {detail.specs.parking_spaces} vagas")
    print(f"Description snippet: {detail.overview.description[:100]}...")


def run_photos_retrieval(client: VeraRentalClient) -> None:
    """Retrieve gallery photos and demonstrate high-resolution conversion."""
    print("\n--- 4. Property Photos Retrieval ---")
    gallery = client.get_photos("1151")
    print(f"Total photos retrieved: {len(gallery)}")
    for idx in range(min(3, len(gallery))):
        print(f"  Photo {idx + 1} (Carousel): {gallery.photo_urls[idx]}")
        print(f"  Photo {idx + 1} (High-Res):  {gallery.high_res_urls[idx]}")


def run_dynamic_neighborhoods(client: VeraRentalClient) -> None:
    """Query dynamic AJAX endpoint for neighborhoods."""
    print("\n--- 5. Dynamic AJAX Neighborhoods Discovery ---")
    bairros = client.get_neighborhoods(
        city_id=int(CityId.TIMOTEO),
        transaction_type=int(TransactionType.ALUGUEL),
    )
    print(f"Total dynamic neighborhoods with rentals in Timóteo: {len(bairros)}")
    for b in bairros:
        print(f"  [{b.numeric_id}] {b.name}")


def run_city_catalog(client: VeraRentalClient) -> None:
    """Discover portal cities."""
    print("\n--- 6. Portal Cities Discovery ---")
    cities = client.get_cities()
    print(f"Total municipalities indexed in search form: {len(cities)}")
    for c in cities:
        print(f"  [{c.numeric_id}] {c.name}")


def main() -> None:
    """Run all verification steps."""
    print("=== Starting Vera Imobiliária Research Verification ===")
    client = VeraRentalClient()
    run_target_search(client)
    run_rental_search(client)
    run_detail_retrieval(client)
    run_photos_retrieval(client)
    run_dynamic_neighborhoods(client)
    run_city_catalog(client)
    print("\n=== All Verification Steps Completed Successfully ===")


if __name__ == "__main__":
    main()
