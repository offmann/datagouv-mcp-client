#!/usr/bin/env python3
"""
Prepare clean JSON data for the Où va votre argent? web app.
Fetches from data.gouv.fr, cleans (no NaN), outputs to app/public/data/
"""

import json
from datetime import datetime, timezone
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("pip install pandas")
    raise

URLS = {
    "skyline": "https://www.data.gouv.fr/fr/datasets/r/4806ff8c-1038-41c3-8547-298980172e09",
    "plf2025": "https://www.data.gouv.fr/fr/datasets/r/b7da87c8-e4e3-4914-8a69-9014f95136d9",
    "recettes": "https://www.data.gouv.fr/fr/datasets/r/8cfff293-a2f3-4885-8262-81533fd71908",
}

OUT_DIR = Path(__file__).parent.parent / "app" / "public" / "data"
STALE_AFTER_DAYS = 14

SOURCE_INFO = {
    "skyline": {
        "label": "Skyline - Comparaison europeenne des depenses publiques",
        "resource_id": "4806ff8c-1038-41c3-8547-298980172e09",
        "resource_url": URLS["skyline"],
        "dataset_url": "https://www.data.gouv.fr/fr/datasets/comparaison-europeenne-des-depenses-publiques/",
    },
    "plf2025": {
        "label": "PLF 2025 - Depenses budgetaires par mission",
        "resource_id": "b7da87c8-e4e3-4914-8a69-9014f95136d9",
        "resource_url": URLS["plf2025"],
        "dataset_url": "https://www.data.gouv.fr/fr/datasets/plf-2025-depenses-budgetaires-de-letat/",
    },
    "recettes": {
        "label": "PLF 2024 - Recettes budgetaires",
        "resource_id": "8cfff293-a2f3-4885-8262-81533fd71908",
        "resource_url": URLS["recettes"],
        "dataset_url": "https://www.data.gouv.fr/fr/datasets/plf-2024-recettes-budgetaires-de-letat/",
    },
}

try:
    from data_pipeline import fetch_csv_with_mcp_fallback, source_fetch_record
except ImportError:
    from scripts.data_pipeline import fetch_csv_with_mcp_fallback, source_fetch_record


def fetch_source(source_key: str) -> tuple[pd.DataFrame, str, str]:
    source = SOURCE_INFO[source_key]
    return fetch_csv_with_mcp_fallback(
        resource_id=source["resource_id"],
        fallback_url=source["resource_url"],
    )


def prepare_skyline() -> tuple[dict, str, str]:
    df, fetch_method, fetch_details = fetch_source("skyline")
    df = df.dropna(subset=["Valeur", "Pays", "Dépense"])
    df["Valeur"] = df["Valeur"].round(2)

    # Use latest year only (avoid summing across years)
    latest_year = df["Année"].max()
    df = df[df["Année"] == latest_year].copy()

    # France by category - use only top-level codes (G1-G5) to avoid double-counting
    top_codes = ["G1", "G2", "G3", "G4", "G5"]
    cat_names = {"G1": "Redistribution (retraites, aides)", "G2": "Services sociaux (santé, éducation)", "G3": "Services généraux (défense, justice)", "G4": "Soutien à l'économie", "G5": "Charge de la dette"}
    fr = df[(df["geo"] == "FR") & (df["Code"].isin(top_codes))].copy()
    fr["Cat"] = fr["Code"].map(cat_names)
    fr_cat = fr.groupby("Cat", as_index=False)["Valeur"].sum()
    fr_cat = fr_cat[fr_cat["Valeur"] > 0].sort_values("Valeur", ascending=False)
    france_by_category = [{"name": r["Cat"], "value": float(round(r["Valeur"], 2))} for _, r in fr_cat.iterrows()]

    # Countries for comparison (main categories G1-G5)
    cat_names_short = {"G1": "Redistribution", "G2": "Services sociaux", "G3": "Services généraux", "G4": "Soutien économie", "G5": "Charge dette"}
    sub = df[df["Code"].isin(top_codes)].copy()
    sub["Cat"] = sub["Code"].map(cat_names_short)
    pivot = sub.pivot_table(index="Pays", columns="Cat", values="Valeur", aggfunc="sum").fillna(0)
    countries = ["France", "Allemagne", "Italie", "Espagne", "Belgique"]
    pivot = pivot.reindex([c for c in countries if c in pivot.index]).dropna(how="all")
    europe_comparison = {country: {str(k): float(v) for k, v in row.items() if v == v} for country, row in pivot.iterrows()}

    return ({
        "france_by_category": france_by_category,
        "europe_comparison": europe_comparison,
        "year": int(latest_year),
    }, fetch_method, fetch_details)


def prepare_budget() -> tuple[dict, str, str]:
    df, fetch_method, fetch_details = fetch_source("plf2025")
    df.columns = [c.strip().lstrip("\ufeff") for c in df.columns]
    cp_col = "credit de paiement"
    mission_col = "libelle mission"
    if cp_col not in df.columns or mission_col not in df.columns:
        return {"missions": [], "total": 0}, fetch_method, fetch_details

    df["_cp"] = pd.to_numeric(df[cp_col], errors="coerce")
    df = df.dropna(subset=["_cp"])
    df = df[df["_cp"] > 0]
    by_mission = df.groupby(mission_col, as_index=False)["_cp"].sum()
    by_mission = by_mission.nlargest(25, "_cp")
    total = float(df["_cp"].sum())
    missions = [{"name": r[mission_col], "value": float(r["_cp"]), "pct": round(100 * r["_cp"] / total, 1)} for _, r in by_mission.iterrows()]

    return {"missions": missions, "total": total}, fetch_method, fetch_details


def prepare_recettes() -> tuple[dict, str, str]:
    df, fetch_method, fetch_details = fetch_source("recettes")
    df["montant"] = pd.to_numeric(df["Montant Recettes PLF"], errors="coerce")
    df = df.dropna(subset=["montant"])
    df = df[df["montant"] > 0]
    df = df[df["Type de recettes"] == "Recettes fiscales"]
    df = df[~df["Libellé"].astype(str).str.match(r"^\d+\.", na=False)]
    df = df[df["Libellé"].astype(str).str.len() < 70]
    by_lib = df.groupby("Libellé", as_index=False)["montant"].sum()
    by_lib = by_lib.nlargest(12, "montant")
    total = float(df["montant"].sum())
    other = total - by_lib["montant"].sum()
    if other > 1e6:
        by_lib = pd.concat([by_lib, pd.DataFrame([{"Libellé": "Autres recettes fiscales", "montant": other}])], ignore_index=True)
    recettes = [{"name": r["Libellé"], "value": float(r["montant"]), "pct": round(100 * r["montant"] / total, 1)} for _, r in by_lib.iterrows()]

    return {"recettes": recettes, "total": total}, fetch_method, fetch_details


def build_metadata(data: dict, fetch_status: dict[str, dict[str, str]]) -> dict:
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    sources = {
        key: source_fetch_record(
            label=source["label"],
            resource_id=source["resource_id"],
            resource_url=source["resource_url"],
            dataset_url=source["dataset_url"],
            fetch_method=fetch_status.get(key, {}).get("method", "unknown"),
            fetch_details=fetch_status.get(key, {}).get("details", "unknown"),
        )
        for key, source in SOURCE_INFO.items()
    }
    years = {
        "skyline": data.get("skyline", {}).get("year"),
        "budget": 2025,
        "recettes": 2024,
    }
    return {
        "generated_at_utc": generated_at,
        "stale_after_days": STALE_AFTER_DAYS,
        "sources": sources,
        "coverage_years": years,
    }


def validate_data_contract(data: dict) -> None:
    required_root = ["skyline", "budget", "recettes", "meta"]
    for key in required_root:
        if key not in data:
            raise ValueError(f"Missing root key: {key}")

    budget = data["budget"]
    recettes = data["recettes"]
    skyline = data["skyline"]
    meta = data["meta"]

    if not isinstance(budget.get("missions"), list) or not budget["missions"]:
        raise ValueError("budget.missions must be a non-empty list")
    if float(budget.get("total", 0)) <= 0:
        raise ValueError("budget.total must be > 0")

    if not isinstance(recettes.get("recettes"), list) or not recettes["recettes"]:
        raise ValueError("recettes.recettes must be a non-empty list")
    if float(recettes.get("total", 0)) <= 0:
        raise ValueError("recettes.total must be > 0")

    pct_budget = sum(float(item.get("pct", 0)) for item in budget["missions"])
    pct_recettes = sum(float(item.get("pct", 0)) for item in recettes["recettes"])
    if not (80 <= pct_budget <= 102):
        raise ValueError(f"budget mission percentages look inconsistent: {pct_budget:.2f}")
    if not (95 <= pct_recettes <= 101):
        raise ValueError(f"recettes percentages look inconsistent: {pct_recettes:.2f}")

    countries = skyline.get("europe_comparison", {})
    if "France" not in countries:
        raise ValueError("skyline.europe_comparison must contain France")
    if not skyline.get("france_by_category"):
        raise ValueError("skyline.france_by_category must be non-empty")

    if not meta.get("generated_at_utc"):
        raise ValueError("meta.generated_at_utc is required")
    if int(meta.get("stale_after_days", 0)) <= 0:
        raise ValueError("meta.stale_after_days must be > 0")
    if not isinstance(meta.get("sources"), dict) or not meta["sources"]:
        raise ValueError("meta.sources must be a non-empty dict")
    for source_key, source_info in meta["sources"].items():
        if not source_info.get("resource_id"):
            raise ValueError(f"meta.sources.{source_key}.resource_id is required")
        if not source_info.get("fetch_method"):
            raise ValueError(f"meta.sources.{source_key}.fetch_method is required")
        if not source_info.get("fetch_details"):
            raise ValueError(f"meta.sources.{source_key}.fetch_details is required")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = {}
    fetch_status: dict[str, dict[str, str]] = {}
    data["skyline"], method, details = prepare_skyline()
    fetch_status["skyline"] = {"method": method, "details": details}
    data["budget"], method, details = prepare_budget()
    fetch_status["plf2025"] = {"method": method, "details": details}
    data["recettes"], method, details = prepare_recettes()
    fetch_status["recettes"] = {"method": method, "details": details}
    data["meta"] = build_metadata(data, fetch_status)
    validate_data_contract(data)
    (OUT_DIR / "public_spending.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"Wrote {OUT_DIR / 'public_spending.json'}")


if __name__ == "__main__":
    main()
