#!/usr/bin/env python3
"""Data pipeline helpers: MCP-first metadata lookup, URL fallback fetch."""

from __future__ import annotations

import io
import sys
import urllib.request
from pathlib import Path
from typing import Any

import pandas as pd

try:
    from datagouv_client import DatagouvClient
except Exception:
    repo_root = Path(__file__).resolve().parent.parent
    src_path = repo_root / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path))
    try:
        from datagouv_client import DatagouvClient
    except Exception:
        DatagouvClient = None


def fetch_csv_via_url(url: str, timeout: int = 30) -> pd.DataFrame:
    with urllib.request.urlopen(url, timeout=timeout) as r:
        content = r.read().decode("utf-8", errors="replace")
    sep = ";" if ";" in content[:500] else ","
    return pd.read_csv(io.StringIO(content), sep=sep)


def fetch_csv_with_mcp_fallback(
    *,
    resource_id: str,
    fallback_url: str,
    timeout: int = 30,
) -> tuple[pd.DataFrame, str, str]:
    """
    Try MCP-compatible client first to resolve resource metadata URL, then fetch CSV.
    Falls back to provided direct URL when MCP path is unavailable.
    """
    if DatagouvClient is not None:
        try:
            client = DatagouvClient(timeout=timeout)
            info = client.get_resource_info(resource_id)
            mcp_url = info.get("url")
            if mcp_url:
                return (
                    fetch_csv_via_url(mcp_url, timeout=timeout),
                    "mcp_resource_info",
                    "resource metadata resolved via datagouv_client.get_resource_info",
                )
            reason = info.get("error") or "missing url in resource metadata"
            details = info.get("details")
            note = f"{reason}; details={details}" if details else reason
            return fetch_csv_via_url(fallback_url, timeout=timeout), "direct_url", note
        except Exception as e:
            return fetch_csv_via_url(fallback_url, timeout=timeout), "direct_url", f"mcp lookup exception: {e}"

    return fetch_csv_via_url(fallback_url, timeout=timeout), "direct_url", "datagouv_client unavailable in environment"


def source_fetch_record(
    *,
    label: str,
    resource_id: str,
    resource_url: str,
    dataset_url: str,
    fetch_method: str,
    fetch_details: str,
) -> dict[str, Any]:
    return {
        "label": label,
        "resource_id": resource_id,
        "resource_url": resource_url,
        "dataset_url": dataset_url,
        "fetch_method": fetch_method,
        "fetch_details": fetch_details,
    }
