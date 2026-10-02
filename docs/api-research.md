# Reverse-Engineered API Specification: Vera Imobiliária

## 1. Overview & Architecture

Vera Imobiliária (`https://www.veraimobiliaria.com.br`) is a real estate portal operating in the Vale do Aço region (Timóteo, Coronel Fabriciano, Ipatinga, and neighboring municipalities in Minas Gerais).

The website backend runs on **Microsoft-IIS/10.0** executing **Classic ASP** (`.asp`) scripts. All server-side responses are delivered as HTML using charset `ISO-8859-1` (Latin1) with session cookie tracking (`ASPSESSIONID...`).

### 1.1 Authentication & Security Requirements
- **Authentication**: **None required**. All property searches, filter options, pagination routes, property details, and image assets are completely publicly accessible without login, session state, API tokens, or CSRF tokens.
- **Request Headers**: Standard desktop `User-Agent` is recommended to prevent IIS security filters from blocking automated requests.
- **HTTP Methods**:
  - Listing searches and property detail retrieval utilize `GET`.
  - Dynamic neighborhood lookup utilizes `POST` (`Request.Form` in Classic ASP).

---

## 2. Rental & Sales Search Endpoints

The search engine accepts HTTP `GET` requests against dedicated search and pagination paths.

### 2.1 Search Routing Patterns

```http
GET /imoveis/busca.html?{query_parameters} HTTP/1.1
Host: www.veraimobiliaria.com.br
```

For paginated requests, the portal maps the page index directly into the URL path:

```http
GET /imoveis/pagina_{page_number}.html?{query_parameters} HTTP/1.1
Host: www.veraimobiliaria.com.br
```

- **Page 1**: `/imoveis/busca.html` or `/imoveis/pagina_1.html`
- **Page N**: `/imoveis/pagina_{N}.html`

---

## 3. Request Parameters & Filter Behavior

The portal form (`<form id="frmbusca" action="imoveis/busca.html" method="get">`) defines the following request parameters:

| Parameter | Type | Required | Example Values | Description & Logic |
| :--- | :--- | :--- | :--- | :--- |
| `txtcdtpnegocioBsc` | `integer` | Yes | `1`, `2` | **Transaction Type**:<br>• `1` = Aluguel (Rental)<br>• `2` = Venda (Sale) |
| `txtcdtpimovelBsc` | `integer` | Yes | `0`, `1`, `3`, `5`... | **Property Category ID**:<br>• `0` = Todos (All)<br>• `1` = Apartamento<br>• `2` = Loja<br>• `3` = Casa<br>• `4` = Lote<br>• `5` = Galpão<br>• `6` = Sala<br>• `7` = Sítio<br>• `8` = Fazenda<br>• `10` = Chácara<br>• `11` = Quitinete<br>• `16` = Cobertura<br>• `17` = Casa Geminada<br>• `18` = Terreno<br>• `21` = Sala-Prédio |
| `txtcdcidadeBsc` | `integer` | Yes | `1`, `2`, `3`... | **Municipality ID**:<br>• `0` = Todas as cidades<br>• `1` = Timóteo<br>• `2` = Coronel Fabriciano<br>• `3` = Ipatinga<br>• `12` = Antônio Dias<br>• `14` = Marliéria<br>• `18` = Jaguaraçu<br>• `21` = Santana do Paraíso<br>• `22` = Córrego Novo |
| `txtcdbairrocidadeBsc` | `integer` | Optional | `11`, `37`, `77`... | **Neighborhood ID**:<br>Numeric neighborhood identifier obtained dynamically from the AJAX endpoint `/asp/ajax/bairros2.asp`. Filters search results strictly to that neighborhood. |
| `faixavalor` | `string` | Yes | `0`, `0a1000`, `1000a3000`, `0a2000` | **Price Range Constraint**:<br>• `0` = Qualquer valor (No filter)<br>• `{min}a{max}` = Interval in BRL (e.g. `1000a3000`).<br>• *Supports arbitrary custom ranges* like `0a2000` or `1400a1600`. |
| `quartos` | `integer` | Yes | `0`, `1`, `2`, `3`, `4`, `5`, `6` | **Bedrooms Parameter**:<br>Form input for bedroom selection. **Important finding**: The IIS backend SQL query ignores this parameter in its WHERE clause. The client module provides client-side domain filtering (`filter_by_min_bedrooms`) to guarantee exact matching for callers. |
| `singlebutton` | `string` | Optional | `""` | Search button submit trigger (empty string). |

---

## 4. Dynamic AJAX Neighborhood Lookup Endpoint

When the user selects a city on the search form, the frontend triggers an AJAX request to populate the neighborhood dropdown `<select name="optcdbairrocidade">`.

### 4.1 AJAX Request Specification
```http
POST /asp/ajax/bairros2.asp HTTP/1.1
Host: www.veraimobiliaria.com.br
Content-Type: application/x-www-form-urlencoded
X-Requested-With: XMLHttpRequest

cidade=1&tpnegocio=1&tpimovel=0&tabindex=18
```

#### Parameters:
- `cidade`: Numeric municipality ID (`1` for Timóteo).
- `tpnegocio`: `1` for rentals, `2` for sales.
- `tpimovel`: Property type ID (`0` for all).
- `tabindex`: Internal index (`18`).

### 4.2 AJAX Response Payload
The server returns raw HTML `<option>` tags, dynamically containing **only** neighborhoods that currently have active listings matching the criteria:

```html
<option data-hidden="false" value="0">Bairro</option>
<option value="11" >Cachoeira+do+Vale</option>
<option value="37" >Centro+Sul</option>
<option value="77" >Primavera</option>
```

> [!NOTE]
> Neighborhood names use URL-encoding with `+` for spaces. The client parser unescapes `+` to standard spaces (e.g. `Cachoeira do Vale`).

---

## 5. Pagination Behavior

- **Page Size**: Fixed at **15 listings per page**.
- **Pagination Mechanism**: Path-based (`/imoveis/pagina_{N}.html?{params}`). Query string parameters (`?pag=2`, `?pagina=2`) are ignored by the backend.
- **Active Page Detection**: In the DOM, active page item is marked `<li class="active"><a>1</a></li>`.
- **Next Page Detection**: Container `<nav class="div-pagination"> <ul class="pagination">` contains `<a href="imoveis/pagina_{N}.html">`. If no higher page link exists, the collection is at the terminal page.
- **Out-of-Bounds Behavior**: Requesting an out-of-bounds page (e.g. `pagina_999.html`) returns HTTP 200 with **0 listing cards** (`len(cards) == 0`).

---

## 6. Search Results Card Parsing

Search result cards are rendered with class `.card` inside responsive columns (`div.col-lg-4`):

### 6.1 DOM Structure
```html
<div class="col-lg-4">
  <div class="card">
    <a href="imovel/1197/galpao_cachoeira-do-vale_timoteo-mg.html">
      <img alt="" class="card-img-top img-fluid" src="imagens/imovel/destaque/1197.png" />
    </a>
    <div class="card-body">
      <div class="row">
        <div class="col-lg-6">
          <span class="preco">R$ 12.000,00</span><br/>
          <span class="endereco">Cachoeira do Vale, Timóteo/MG</span>
        </div>
        <div class="col-lg-6 icones">
          <div class="col-4">
            <img class="img-fluid" src="./img/cama.png"/>
            <span>0</span>
          </div>
          <div class="col-4">
            <img class="img-fluid" src="./img/chuveiro.png"/>
            <span>0</span>
          </div>
          <div class="col-4">
            <img class="img-fluid" src="./img/carro.png"/>
            <span>0</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```

### 6.2 Field Extraction Matrix
| Domain Field | DOM Selector / Regex | Example Extracted Value |
| :--- | :--- | :--- |
| `property_id` | `card.find("a")['href']` regex `imovel/(\d+)` | `"1197"` |
| `url_path` | `card.find("a")['href']` | Original source `href`, retained unchanged |
| `url` | Resolve a valid property-route `href` against the configured public base; an absent link falls back to `/imovel/{property_id}.html` | Absolute URL restricted to the same host and `/imovel/{id}` property routes; search, AJAX, and image destinations are rejected |
| `thumbnail_url` | `card.find("img", class_="card-img-top")['src']` | `"imagens/imovel/destaque/1197.png"` |
| `price_text` | `span.preco` text | `"R$ 12.000,00"` |
| `price_numeric` | regex `R\$\s*([\d\.,]+)` parsed as float | `12000.0` |
| `neighborhood` | `span.endereco` text before `,` | `"Cachoeira do Vale"` |
| `city` | `span.endereco` text between `,` and `/` | `"Timóteo"` |
| `state` | `span.endereco` text after `/` | `"MG"` |
| `bedrooms` | `img[src*='cama']` parent `span` text | `0` (or `4` for residential) |
| `bathrooms` | `img[src*='chuveiro']` parent `span` text | `0` (or `2`) |
| `parking_spaces` | `img[src*='carro']` parent `span` text | `0` (or `1`) |

---

## 7. Property Detail Retrieval

Full property specifications are accessible via direct property ID URLs.

### 7.1 Detail Endpoints
- **Canonical Endpoint**: `GET https://www.veraimobiliaria.com.br/imovel/{property_id}.html`
- **Slug Endpoint**: `GET https://www.veraimobiliaria.com.br/imovel/{property_id}/{slug}.html`
- Both URLs resolve identically; the backend router relies only on the numeric `{property_id}`.
- **Non-Existent ID Handling**: Returns HTTP 200 with empty detail containers. The parser validates the presence of property content and raises `PropertyNotFoundError`.

### 7.2 Detail Field Extraction Matrix
| Field | Selector / Extraction Logic | Example Value |
| :--- | :--- | :--- |
| `title` | `div.titulo` text | `"CASA - ALUGUEL - Primavera, Timóteo/MG"` |
| `price_text` | `div.detalhes h1` text | `"R$ 2.500,00"` |
| `price_numeric` | regex `R\$\s*([\d\.,]+)` parsed as float | `2500.0` |
| `iptu_text` | regex `IPTU[^\:]*:\s*([^\n\r]+)` from `div#detalhes` | `"Consultar"` |
| `condominio_text` | regex `Condom[íi]nio[^\:]*:\s*([^\n\r]+)` from `div#detalhes` | `"Consultar"` |
| `address` | `div.localizacao a` text | `"Não infor. , 0, Primavera - Timóteo/MG"` |
| `map_url` | `div.localizacao a['href']` | `"https://www.google.com/maps/search/..."` |
| `neighborhood` | parsed from address text | `"Primavera"` |
| `city` / `state` | parsed from address text | `"Timóteo"` / `"MG"` |
| `bedrooms` | `img[src*='cama']` sibling text | `4` |
| `bathrooms` | `img[src*='chuveiro']` sibling text | `2` |
| `parking_spaces` | `img[src*='carro']` sibling text | `1` |
| `built_area` | regex `Área construída:\s*([^\n\r]+)` | `"não informado"` |
| `lot_area` | regex `Área do lote:\s*([^\n\r]+)` | `"não informado"` |
| `description` | `div#detalhes .col-lg-4` second column text | `"4 quartos sendo 1 uma suíte\nSala..."` |
| `features` | list of non-empty feature lines | `("4 quartos sendo 1 uma suíte", "Sala", ...)` |

---

## 8. Photo Gallery & Resolution Architecture

The detail page embeds a responsive carousel using Owl Carousel (`div#owl-carousel`).

### 8.1 Carousel Image Structure
```html
<div class="owl-carousel owl-theme">
  <div class="item"><img src="imagens/imovel/1151/m/0005.jpeg" /></div>
  <div class="item"><img src="imagens/imovel/1151/m/0006.jpeg" /></div>
  ...
</div>
```

### 8.2 Image URL Resolution
- **Carousel / Medium Image**:
  `https://www.veraimobiliaria.com.br/imagens/imovel/{id}/m/{photo_filename}`
- **High-Resolution (Grande) Image**:
  Replacing `/m/` with `/g/` in the path yields the full-resolution uncompressed photo:
  `https://www.veraimobiliaria.com.br/imagens/imovel/{id}/g/{photo_filename}`
- **Featured Thumbnail**:
  `https://www.veraimobiliaria.com.br/imagens/imovel/destaque/{id}.png`

---

## 9. Target URL Reproduction Analysis

### Target URL from User Prompt
`https://www.veraimobiliaria.com.br/imoveis/busca.html?txtcdtpnegocioBsc=1&txtcdtpimovelBsc=0&txtcdcidadeBsc=1&faixavalor=0&quartos=2&singlebutton=`

### Parameter Decomposition
1. `txtcdtpnegocioBsc=1`: Transaction purpose: **Aluguel (Rental)**.
2. `txtcdtpimovelBsc=0`: Property category: **Todos (All property types)**.
3. `txtcdcidadeBsc=1`: Municipality: **Timóteo**.
4. `faixavalor=0`: Price range: **Qualquer valor (Unrestricted)**.
5. `quartos=2`: Bedrooms: **2 quartos**.
6. `singlebutton=`: Standard form submit trigger.

### Live Server Behavior & Reproduction
Executing this query against the live server returns all active rental listings in Timóteo:
- `1197`: Galpão Comercial (Cachoeira do Vale) — R$ 12.000,00
- `1232`: Sala Prédio (Centro Sul) — R$ 1.500,00
- `1151`: Casa Residencial (Primavera, 4 quartos) — R$ 2.500,00

To enforce strict bedroom count matching when requested by callers, the client facade provides client-side domain filtering:
```python
results = client.search(criteria, apply_bedroom_filter=True)
```

---

## 10. Python Central Rental Research MCP Client Integration

The reverse-engineered endpoints are encapsulated in the `vera_research` package, providing clean interfaces suitable for integration into the central rental research MCP:

```python
from vera_research import VeraRentalClient, SearchCriteria, PropertyType, CityId

client = VeraRentalClient()

# 1. Search rental listings in Timóteo
rentals = client.search_rentals(city_id=int(CityId.TIMOTEO))
for listing in rentals:
    print(f"[{listing.identity.property_id}] {listing.title} - {listing.price_text}")
    print(f"  Link: {listing.identity.url}")

# Typed search collections also serialize with `to_dictionary()` while retaining
# integer `current_page`, boolean `has_next_page`, and each source `url_path`.
search_payload = rentals.to_dictionary()

# 2. Retrieve property details
details = client.get_details("1151")
print(f"Title: {details.overview.title}")
print(f"Price: R$ {details.pricing.amount:,.2f}")
print(f"Location: {details.location.neighborhood}, {details.location.city}")
print(f"Rooms: {details.specs.bedrooms} dorms, {details.specs.bathrooms} banheiros")

# 3. Retrieve property gallery photos (medium and high-resolution)
photos = client.get_photos("1151")
print(f"Loaded {len(photos)} photos.")
print(f"Lead Carousel: {photos.first_photo()}")
print(f"Lead High-Res:  {photos.first_high_res_photo()}")

# 4. Discover dynamic neighborhoods with active rental listings
neighborhoods = client.get_neighborhoods(city_id=int(CityId.TIMOTEO))
for b in neighborhoods:
    print(f"Neighborhood [{b.numeric_id}]: {b.name}")
```
