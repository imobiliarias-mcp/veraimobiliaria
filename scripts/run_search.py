#!/usr/bin/env python3
"""CLI utility to execute searches on Vera Imobiliária portal."""

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from vera_research import (
    CityId,
    PropertyType,
    TransactionType,
    VeraRentalClient,
)


def main() -> None:
    """Run CLI search."""
    parser = argparse.ArgumentParser(description="Vera Imobiliária Search Runner")
    parser.add_argument("--city", type=int, default=int(CityId.TIMOTEO), help="City ID (1=Timóteo, 2=Fabriciano, 3=Ipatinga)")
    parser.add_argument("--transaction", type=int, default=int(TransactionType.ALUGUEL), help="1=Aluguel, 2=Venda")
    parser.add_argument("--type", type=int, default=int(PropertyType.TODOS), help="Property type ID (0=Todos, 1=Apto, 3=Casa)")
    parser.add_argument("--bedrooms", type=int, default=None, help="Bedrooms filter")
    parser.add_argument("--min-price", type=int, default=None, help="Minimum price in BRL")
    parser.add_argument("--max-price", type=int, default=None, help="Maximum price in BRL")
    parser.add_argument("--page", type=int, default=1, help="Page number (1-indexed)")
    parser.add_argument("--filter-bedrooms", action="store_true", help="Apply strict client-side bedroom filter")

    args = parser.parse_args()
    client = VeraRentalClient()

    print(f"Searching: transaction={args.transaction}, city={args.city}, type={args.type}, page={args.page}...")
    results = client.search_rentals(
        city_id=args.city,
        property_type=PropertyType(args.type),
        bedrooms=args.bedrooms,
        min_price=args.min_price,
        max_price=args.max_price,
        page=args.page,
        apply_bedroom_filter=args.filter_bedrooms,
    )

    print(f"Found {len(results)} listings (Page {results.current_page}, next_page={results.has_next_page}):")
    for item in results:
        print(f"  [{item.identity.property_id}] {item.title[:40]} | {item.price_text} | {item.location.neighborhood} | Bed: {item.specs.bedrooms}")
        print(f"    Link: {item.identity.url}")


if __name__ == "__main__":
    main()
