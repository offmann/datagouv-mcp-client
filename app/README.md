# Where Does Your Money Go? - Web App

Citizen-facing web app that explains how French public money is collected and spent.

## Start

1. Prepare data (from repository root):
   ```bash
   uv run python scripts/prepare_data.py
   uv run python scripts/validate_data_contract.py
   ```
2. Run the app:
   ```bash
   cd app && npm install && npm run dev
   ```
3. Open http://localhost:5173

## Data used

- Tax revenues: PLF 2024 (data.gouv.fr)
- Budget missions: PLF 2025 (data.gouv.fr)
- Europe comparison: Skyline public spending dataset
- Metadata contract:
  - freshness (`generated_at_utc`, `stale_after_days`)
  - source provenance (`resource_id`, `resource_url`, `dataset_url`)
  - fetch trace (`fetch_method`, `fetch_details`)

## Stack

- React + Vite
- Tailwind CSS
- Recharts
