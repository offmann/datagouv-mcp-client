# AGENTS.md – Guide for coding agents

This document helps AI coding agents understand and iterate on this project. Read it before making changes.

---

## Project overview

**datagouv-mcp-client** has three connected parts:

1. **Python MCP client** (`src/datagouv_client/`) – MCP-compatible client for [data.gouv.fr](https://www.data.gouv.fr) API (search datasets, get metadata, download resources).
2. **Data pipeline** (`scripts/`) – Fetches data.gouv.fr CSVs, cleans them, outputs JSON. Uses the MCP client when available for resource URL resolution; falls back to direct URLs.
3. **Web app** (`app/`) – Interactive citizen app **« Où va votre argent ? »** that visualizes where public money goes. Consumes the pre-generated JSON only (no Python at runtime).

---

## Architecture: how the pieces connect

```
┌─────────────────────────────────────────────────────────────────────────┐
│  DATA SOURCES (data.gouv.fr)                                             │
│  Skyline CSV | PLF 2025 dépenses CSV | PLF 2024 recettes CSV             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  scripts/data_pipeline.py                                                │
│  fetch_csv_with_mcp_fallback(resource_id, fallback_url)                 │
│  • Tries: DatagouvClient.get_resource_info(resource_id) → get URL       │
│  • Falls back: direct fallback_url if client unavailable or lookup fails│
│  • Always fetches CSV via HTTP (urllib), returns (DataFrame, method, …) │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  scripts/prepare_data.py                                                 │
│  Uses data_pipeline for each source → cleans → aggregates → JSON        │
│  Output: app/public/data/public_spending.json (with meta.sources, etc.)  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  app/ (React + Vite)                                                    │
│  Fetches /data/public_spending.json at load → renders charts, calculator │
│  No Python, no MCP, no datagouv_client at runtime                       │
└─────────────────────────────────────────────────────────────────────────┘
```

**Summary:** The MCP client is used during data preparation (via `data_pipeline`) for metadata lookup. The web app never touches Python or the client; it only reads static JSON.

**"Are we using the MCP client or not?"** – Yes, when preparing data: `data_pipeline` calls `DatagouvClient.get_resource_info(resource_id)` to resolve the download URL. If the client is unavailable (import fails, API error), it falls back to hardcoded URLs. The web app itself does not use the client.

---

## Quick start (for agents)

```bash
# 1. Prepare data (required before running app)
uv run python scripts/prepare_data.py

# 2. Validate JSON contract (optional)
uv run python scripts/validate_data_contract.py

# 3. Run the web app
cd app && npm install && npm run dev
# Open http://localhost:5173 (or the port shown)
```

---

## Repository structure

```
datagouv-mcp-client/
├── AGENTS.md                    # This file
├── README.md                    # User-facing docs
├── pyproject.toml               # Python package (uv)
├── .python-version              # 3.13
├── src/datagouv_client/         # Python MCP client (datasets, resources, schemas)
├── scripts/
│   ├── data_pipeline.py         # MCP-first fetch: get_resource_info → URL → CSV
│   ├── prepare_data.py          # Orchestrates fetch, clean, aggregate, write JSON
│   └── validate_data_contract.py # Validates public_spending.json schema
├── app/                         # React + Vite web app
│   ├── public/data/             # public_spending.json (generated)
│   ├── src/
│   │   ├── App.jsx
│   │   ├── index.css            # Tailwind v4 + @theme
│   │   └── components/          # Hero, Nav, TaxCalculator, PersonalImpact,
│   │                            # BudgetTreemap, BudgetExplorer, RevenueBreakdown,
│   │                            # EuroAllocation, EuropeChart
│   ├── postcss.config.js        # @tailwindcss/postcss (Tailwind v4)
│   └── package.json
├── docs/
│   ├── data_pipeline_modes.md   # mcp_resource_info vs direct_url
│   └── public_spending_data_inventory.md
├── examples/
│   └── public_spending_plots.py # Legacy matplotlib plots (optional)
└── output/                      # Static plot outputs (gitignored)
```

---

## Data flow (detailed)

1. **`scripts/data_pipeline.py`** – `fetch_csv_with_mcp_fallback(resource_id, fallback_url)`:
   - If `DatagouvClient` is available: calls `client.get_resource_info(resource_id)` to get the resource’s download URL.
   - If URL is found: fetches CSV from that URL, returns `(df, "mcp_resource_info", details)`.
   - Otherwise: fetches from `fallback_url`, returns `(df, "direct_url", reason)`.

2. **`scripts/prepare_data.py`** – For each source (skyline, plf2025, recettes):
   - Calls `fetch_source(key)` → `fetch_csv_with_mcp_fallback(...)`.
   - Cleans and aggregates the DataFrame.
   - Builds `meta` (generated_at_utc, sources with fetch_method/fetch_details).
   - Writes `app/public/data/public_spending.json`.

3. **App** – Loads `/data/public_spending.json`, uses `skyline`, `budget`, `recettes`, `meta` (e.g. staleness, source provenance).

**JSON shape:** See `prepare_data.py` and `validate_data_contract.py` for the full contract. Root keys: `skyline`, `budget`, `recettes`, `meta`.

---

## Tech stack

| Layer | Tech |
|-------|------|
| Python client | httpx, pandas, Python 3.13 |
| Data pipeline | pandas, datagouv_client (optional) |
| App | React 19, Vite 7 |
| Styling | Tailwind CSS v4 (`@tailwindcss/postcss`, `@theme` in CSS) |
| Charts | Recharts |

**Tailwind v4:** No `tailwind.config.js`. Theme in `app/src/index.css` via `@theme`. PostCSS uses `@tailwindcss/postcss` only.

---

## Key files to edit

| Goal | File(s) |
|------|---------|
| Add/change data sources | `scripts/prepare_data.py` (SOURCE_INFO, fetch_source calls) |
| Change fetch logic (MCP vs URL) | `scripts/data_pipeline.py` |
| Change JSON shape | `scripts/prepare_data.py`, `scripts/validate_data_contract.py`, then app components |
| Add chart/section | `app/src/App.jsx`, new component in `app/src/components/` |
| Styling / theme | `app/src/index.css` (`@theme`, `:root`) |
| Data inventory / URLs | `docs/public_spending_data_inventory.md` |

---

## Conventions

- **French UI** – All user-facing text in French.
- **formatEuro(n)** – For amounts (Md€, M€, k€). Define locally or share via util.
- **Colors** – `bleu`, `bleu-dark`, `rouge`, `creme`, `noir` in Tailwind/CSS.
- **Fonts** – DM Sans (body), Playfair Display (headings). Google Fonts in `index.html`.

---

## Known limitations & improvement ideas

1. **Tax calculator** – Flat 25% rate; could use real brackets.
2. **Data freshness** – Manual `prepare_data.py`; no CI or auto-refresh.
3. **MCP usage** – Only `get_resource_info` for URL resolution; `download_resource` is not used in the pipeline.
4. **direct_url mode** – Normal when MCP/client unavailable; see `docs/data_pipeline_modes.md`.
5. **Mobile** – Charts may overflow on small screens.
6. **Accessibility** – Add ARIA, keyboard nav, chart alternatives.

---

## Testing changes

```bash
uv run python scripts/prepare_data.py
uv run python scripts/validate_data_contract.py
cd app && npm run build
```

---

## Data source URLs (for reference)

- Skyline: `https://www.data.gouv.fr/fr/datasets/r/4806ff8c-1038-41c3-8547-298980172e09`
- PLF 2025 dépenses: `https://www.data.gouv.fr/fr/datasets/r/b7da87c8-e4e3-4914-8a69-9014f95136d9`
- PLF 2024 recettes: `https://www.data.gouv.fr/fr/datasets/r/8cfff293-a2f3-4885-8262-81533fd71908`

Full inventory: `docs/public_spending_data_inventory.md`.
