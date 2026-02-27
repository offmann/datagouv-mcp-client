"""Dataset and dataservice tools – search, info, resources."""

from typing import Any

import httpx


def search_datasets(
    base_url: str, query: str, page: int = 1, page_size: int = 20, timeout: int = 30
) -> dict:
    """Search datasets on data.gouv.fr. Use short, specific queries (API uses AND logic)."""
    resp = httpx.get(
        f"{base_url}/datasets/",
        params={"q": query, "page": page, "page_size": page_size},
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()
    items = data.get("data", [])
    return {
        "datasets": [
            {
                "id": d.get("id"),
                "title": d.get("title"),
                "slug": d.get("slug"),
                "organization": d.get("organization", {}).get("name") if d.get("organization") else None,
                "resources_count": len(d.get("resources", [])),
            }
            for d in items
        ],
        "page": data.get("page", 1),
        "total": data.get("total", 0),
    }


def get_dataset_info(base_url: str, dataset_id: str, timeout: int = 30) -> dict:
    """Get dataset metadata: title, description, organization, resources."""
    resp = httpx.get(f"{base_url}/datasets/{dataset_id}/", timeout=timeout)
    resp.raise_for_status()
    d = resp.json()
    return {
        "id": d.get("id"),
        "title": d.get("title"),
        "slug": d.get("slug"),
        "description": (d.get("description") or "")[:1000],
        "organization": d.get("organization", {}).get("name") if d.get("organization") else None,
        "license": d.get("license"),
        "page": d.get("page"),
        "resources_count": len(d.get("resources", [])),
        "resources": [
            {"id": r.get("id"), "title": r.get("title"), "format": r.get("format"), "url": r.get("url")}
            for r in d.get("resources", [])[:50]
        ],
    }


def list_dataset_resources(base_url: str, dataset_id: str, timeout: int = 30) -> dict:
    """List all resources in a dataset."""
    info = get_dataset_info(base_url, dataset_id, timeout)
    return {
        "dataset_id": dataset_id,
        "dataset_title": info.get("title"),
        "resources": info.get("resources", []),
        "total": len(info.get("resources", [])),
    }


def search_dataservices(
    base_url: str, query: str, page: int = 1, page_size: int = 20, timeout: int = 30
) -> dict:
    """Search dataservices (API catalog) on data.gouv.fr."""
    try:
        resp = httpx.get(
            f"{base_url}/dataservices/",
            params={"q": query, "page": page, "page_size": page_size},
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        items = data.get("data", [])
        return {
            "dataservices": [
                {
                    "id": d.get("id"),
                    "title": d.get("title"),
                    "organization": d.get("organization", {}).get("name") if d.get("organization") else None,
                    "base_api_url": d.get("base_api_url"),
                }
                for d in items
            ],
            "total": data.get("total", 0),
        }
    except httpx.HTTPStatusError as e:
        return {"error": f"Dataservices API unavailable: {e}", "dataservices": [], "total": 0}


def get_dataservice_info(base_url: str, dataservice_id: str, timeout: int = 30) -> dict:
    """Get dataservice metadata."""
    try:
        resp = httpx.get(f"{base_url}/dataservices/{dataservice_id}/", timeout=timeout)
        resp.raise_for_status()
        d = resp.json()
        return {
            "id": d.get("id"),
            "title": d.get("title"),
            "description": (d.get("description") or "")[:500],
            "organization": d.get("organization", {}).get("name") if d.get("organization") else None,
            "base_api_url": d.get("base_api_url"),
            "machine_documentation_url": d.get("machine_documentation_url"),
        }
    except httpx.HTTPStatusError as e:
        return {"error": str(e)}
