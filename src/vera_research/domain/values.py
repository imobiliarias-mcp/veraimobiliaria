"""Domain value objects representing search parameters and constraints."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PriceRange:
    """Encapsulates price constraints formatted for the faixavalor parameter."""

    minimum: int | None = None
    maximum: int | None = None

    def __post_init__(self) -> None:
        """Validate price values."""
        if self.minimum is not None and self.minimum < 0:
            raise ValueError("Minimum price cannot be negative")
        if self.maximum is not None and self.maximum < 0:
            raise ValueError("Maximum price cannot be negative")

    def to_faixavalor_code(self) -> str:
        """Convert price range to portal faixavalor format."""
        if self.minimum is None and self.maximum is None:
            return "0"
        min_val = self.minimum if self.minimum is not None else 0
        max_val = self.maximum if self.maximum is not None else 100000000000
        return f"{min_val}a{max_val}"


@dataclass(frozen=True)
class RoomCount:
    """Represents a bedroom count constraint."""

    count: int = 0

    def __post_init__(self) -> None:
        """Enforce non-negative room count."""
        if self.count < 0:
            raise ValueError("Room count cannot be negative")

    def to_param_code(self) -> str:
        """Return the string parameter for the search query."""
        return str(self.count)


@dataclass(frozen=True)
class PageNumber:
    """Represents a 1-indexed pagination number."""

    value: int = 1

    def __post_init__(self) -> None:
        """Enforce positive page index."""
        if self.value < 1:
            raise ValueError("Page index must be greater than or equal to 1")

    def to_path_segment(self) -> str:
        """Return URL path segment for pagination."""
        if self.value == 1:
            return "imoveis/busca.html"
        return f"imoveis/pagina_{self.value}.html"
