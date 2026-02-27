#!/usr/bin/env python3
"""Validate app/public/data/public_spending.json contract."""

import json
from pathlib import Path

from prepare_data import validate_data_contract


def main() -> None:
    json_path = Path(__file__).parent.parent / "app" / "public" / "data" / "public_spending.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))
    validate_data_contract(data)
    print(f"Contract OK: {json_path}")


if __name__ == "__main__":
    main()
