# Data Pipeline Modes (MCP vs Direct URL)

This project supports two fetch modes per source when generating `app/public/data/public_spending.json`.

## Modes

- `mcp_resource_info`
  - The pipeline resolves resource metadata through the Python MCP-compatible client (`DatagouvClient.get_resource_info`).
  - It then fetches the CSV from the resolved URL.
- `direct_url`
  - The pipeline falls back to the configured stable Data.gouv resource URL.
  - This is expected behavior when MCP metadata lookup is unavailable or does not return a usable `url`.

## Why this matters

- `mcp_resource_info` is useful for dynamic discovery and richer metadata workflows.
- `direct_url` is a stable and valid operational mode for this app.
- The app should not be considered broken when `direct_url` appears, as long as data generation and validation succeed.

## How to inspect mode and reason

Run:

```bash
uv run python scripts/prepare_data.py
jq -r '.meta.sources | to_entries[] | "\(.key): \(.value.fetch_method) | \(.value.fetch_details)"' app/public/data/public_spending.json
```

Each source includes:

- `fetch_method`: selected mode
- `fetch_details`: diagnostic reason for the selected mode

## Recommended interpretation

- Prefer correctness and freshness first (`prepare_data.py` + contract validation pass).
- Treat `direct_url` as acceptable unless you explicitly need dynamic resource discovery behavior from MCP metadata endpoints.
