"""Unit tests for VeraMcpAdapter."""

from scripts.mcp.tools import VeraMcpAdapter


class DummyClient:
    """Dummy client for testing Vera MCP adapter."""

    def search_rentals(self, **kwargs):
        class DummyListing:
            price_text = "R$ 1.400"
            title = "Apto Vera Centro"
            class identity:
                property_id = "777"
                url = "https://www.veraimobiliaria.com.br/imovel/777"
            class location:
                neighborhood = "Centro"
                city = "Timóteo"
            class specs:
                bedrooms = 2
                bathrooms = 1
        class DummyCollection(list):
            pass
        return DummyCollection([DummyListing()])

    def get_details(self, ref):
        class DummyDetail:
            canonical_url = f"https://www.veraimobiliaria.com.br/imovel/{ref}"
            features = []
            class overview:
                property_id = ref
                title = "Apto Vera Centro"
            class pricing:
                formatted_text = "R$ 1.400"
            class location:
                neighborhood = "Centro"
                city = "Timóteo"
                state = "MG"
            class specs:
                bedrooms = 2
                bathrooms = 1
                parking_spaces = 1
                usable_area = 85.0
            class photos:
                photo_urls = ["https://www.veraimobiliaria.com.br/foto1.jpg"]
        return DummyDetail()

    def get_cities(self):
        class DummyCityCatalog:
            cities = []
        return DummyCityCatalog()


def test_mcp_adapter_provider_info():
    """Test MCP provider metadata."""
    adapter = VeraMcpAdapter(client=DummyClient())
    info = adapter.get_provider_info()
    assert info["provider_name"] == "veraimobiliaria"
    assert "search_rentals" in info["supported_operations"]


def test_mcp_adapter_search_rentals():
    """Test MCP search tool execution."""
    adapter = VeraMcpAdapter(client=DummyClient())
    res = adapter.search_rentals(city="Timóteo", bedrooms=2, max_price=1500.0)
    assert isinstance(res, dict)
    assert res["provider"] == "veraimobiliaria"
    assert len(res["listings"]) == 1


def test_mcp_adapter_property_detail():
    """Test MCP property detail tool execution."""
    adapter = VeraMcpAdapter(client=DummyClient())
    detail = adapter.get_property_detail("777")
    assert isinstance(detail, dict)
    assert detail["title"] == "Apto Vera Centro"
