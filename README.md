# Vera Imobiliária — Central Rental Research MCP Provider

Reverse-engineered rental search engine and API client for **Vera Imobiliária** (`https://www.veraimobiliaria.com.br/`).

Engineered as a pluggable adapter for the **Central Rental Research MCP (Model Context Protocol)** module following **SOLID**, **Clean Code**, **Object Calisthenics**, and **Design Patterns** in Python, operating as a sister provider to **Epifânio Imóveis** and **Casa Linhares**.

---

## 📚 Documentation

- **[Documentation Index](file:///home/samuelcaldas/repos/imobiliarias/veraimobiliaria/docs/README.md)** (`docs/README.md`): Overview of project documentation.
- **[Reverse Engineering Analysis & API Specification](file:///home/samuelcaldas/repos/imobiliarias/veraimobiliaria/docs/api-research.md)** (`docs/api-research.md`): Reverse-engineered endpoint specification, parameter matrices, dynamic AJAX endpoints, and DOM extraction selectors.
- **[Research Plan & Findings Report](file:///home/samuelcaldas/repos/imobiliarias/veraimobiliaria/scripts/research-plan.md)** (`scripts/research-plan.md`): Research methodology, discovery findings, architectural design, and test execution results.

---

## ⚡ Quickstart

### Run Automated Tests
```bash
uv run pytest -v
```

### Run Full Verification Script
```bash
uv run python scripts/verify_research.py
```

### Search Rentals via CLI
```bash
# Search rentals in Timóteo
uv run python scripts/run_search.py --city 1

# Search rentals with bedrooms and price filter
uv run python scripts/run_search.py --city 1 --bedrooms 2 --max-price 3000
```

### View Listing Details via CLI
```bash
# View complete details for property code 1151
uv run python scripts/run_property_detail.py 1151
```

---

## 🏛️ Code Architecture & Standards Compliance

- **Priority Order**: Correctness first, Modularity second, Style principles third.
- **No `else` Keyword**: 100% eliminated using guard clauses, early returns, and polymorphic handlers.
- **Single Level of Indentation**: All methods adhere strictly to at most 1 indent level.
- **Wrapped Primitives**: Domain concepts (`PriceRange`, `RoomCount`, `PageNumber`) are immutable Value Objects.
- **First-Class Collections**: `ListingCollection`, `PhotoGallery`, `NeighborhoodCatalog`, and `CityCatalog` wrap items without exposing raw mutable lists.
- **Entity Size Limits**: Functions $\le$ 15 lines, Classes $\le$ 100 lines, Modules $<$ 200 lines.
- **Instance Variables**: All classes hold at most 2 instance variables.
- **Zero Abbreviations**: Clear, descriptive domain naming across all modules.
