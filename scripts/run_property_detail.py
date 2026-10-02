#!/usr/bin/env python3
"""CLI utility to retrieve full property details from Vera Imobiliária portal."""

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from vera_research import VeraRentalClient


def main() -> None:
    """Run CLI property detail retrieval."""
    parser = argparse.ArgumentParser(description="Vera Imobiliária Property Detail Runner")
    parser.add_argument("property_id", type=str, help="Property ID (e.g. 1151, 1197, 1232)")
    args = parser.parse_args()

    client = VeraRentalClient()
    print(f"Fetching details for property ID {args.property_id}...")

    detail = client.get_details(args.property_id)
    print("\n=== Property Detail ===")
    print(f"ID:           {detail.overview.property_id}")
    print(f"Title:        {detail.overview.title}")
    print(f"Price:        {detail.pricing.formatted_text} (Amount: {detail.pricing.amount})")
    print(f"IPTU:         {detail.pricing.iptu_text}")
    print(f"Condomínio:   {detail.pricing.condominio_text}")
    print(f"Address:      {detail.location.address}")
    print(f"Neighborhood: {detail.location.neighborhood}")
    print(f"City/State:   {detail.location.city} - {detail.location.state}")
    print(f"Map URL:      {detail.location.map_url}")
    print(f"Bedrooms:     {detail.specs.bedrooms}")
    print(f"Bathrooms:    {detail.specs.bathrooms}")
    print(f"Parking:      {detail.specs.parking_spaces}")
    print(f"Built Area:   {detail.specs.built_area}")
    print(f"Lot Area:     {detail.specs.lot_area}")
    print(f"Photos:       {len(detail.photos)} photos loaded")
    if detail.photos.first_photo():
        print(f"Lead Photo:   {detail.photos.first_photo()}")
        print(f"High-Res:     {detail.photos.first_high_res_photo()}")

    print("\n--- Description ---")
    print(detail.overview.description)


if __name__ == "__main__":
    main()
