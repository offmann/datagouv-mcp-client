"""Resource tools – info, download, parse."""

from io import BytesIO

import httpx
import pandas as pd


def get_resource_info(base_url: str, resource_id: str, timeout: int = 30) -> dict:
    """
    Get resource metadata. Uses data.gouv.fr API.
    If direct lookup fails, use list_dataset_resources to get resource from a dataset.
    """
    endpoints = [
        f"{base_url}/datasets/r/{resource_id}/",
        f"{base_url}/datasets/resources/{resource_id}/",
    ]

    errors: list[str] = []
    for endpoint in endpoints:
        try:
            resp = httpx.get(endpoint, timeout=timeout)
            resp.raise_for_status()
            r = resp.json()
            return {
                "id": r.get("id") or resource_id,
                "title": r.get("title"),
                "format": r.get("format"),
                "url": r.get("url"),
                "filesize": r.get("filesize"),
                "mime_type": r.get("mime") or r.get("mime_type"),
            }
        except httpx.HTTPStatusError as e:
            errors.append(f"{endpoint} -> HTTP {e.response.status_code}")
        except Exception as e:
            errors.append(f"{endpoint} -> {e}")

    return {
        "error": "Resource metadata not found from known endpoints.",
        "id": resource_id,
        "details": errors,
    }


def download_resource(
    base_url: str,
    resource_id: str,
    timeout: int = 30,
    max_rows: int | None = None,
    max_size_mb: int = 500,
) -> dict:
    """
    Download and parse a resource. Supports CSV, JSON, JSONL, Parquet.

    For large files, use max_rows to limit. Data stays on data.gouv.fr servers;
    we only fetch what we need for parsing.
    """
    meta = get_resource_info(base_url, resource_id, timeout)
    if meta.get("error"):
        return meta
    url = meta.get("url")
    if not url:
        return {"error": "No download URL in resource metadata", "meta": meta}

    # Fetch content
    r = httpx.get(url, follow_redirects=True, timeout=timeout)
    r.raise_for_status()
    content = r.content
    size_mb = len(content) / (1024 * 1024)
    if size_mb > max_size_mb:
        return {"error": f"Resource too large ({size_mb:.1f}MB > {max_size_mb}MB)", "meta": meta}

    fmt = (meta.get("format") or "").lower()
    rows: list[dict] = []

    try:
        if fmt in ("csv", "tsv"):
            df = pd.read_csv(BytesIO(content), sep=";" if ";" in content[:500].decode("utf-8", errors="ignore") else ",", nrows=max_rows, low_memory=False)
            rows = df.head(max_rows or 100).to_dict(orient="records")
        elif fmt == "json":
            import json
            data = json.loads(content)
            if isinstance(data, list):
                rows = data[: max_rows or 100]
            elif isinstance(data, dict):
                rows = [data]
            else:
                rows = [{"data": str(data)[:500]}]
        elif fmt == "jsonl":
            import json
            lines = content.decode("utf-8", errors="ignore").strip().split("\n")[: max_rows or 100]
            rows = [json.loads(l) for l in lines if l]
        elif "parquet" in fmt or url.endswith(".parquet"):
            df = pd.read_parquet(BytesIO(content))
            rows = df.head(max_rows or 100).to_dict(orient="records")
        else:
            return {"error": f"Unsupported format: {fmt}", "meta": meta, "url": url}
    except Exception as e:
        return {"error": str(e), "meta": meta, "url": url}

    return {
        "meta": meta,
        "rows": rows,
        "row_count": len(rows),
    }
