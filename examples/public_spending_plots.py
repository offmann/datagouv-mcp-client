#!/usr/bin/env python3
"""
Public spending visualization – data from data.gouv.fr

Fetches public money (taxes, budget) data and creates publication-ready plots.
Requires: pip install pandas matplotlib httpx
"""

import io
import urllib.request
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Data.gouv.fr resource URLs
SKYLINE_URL = "https://www.data.gouv.fr/fr/datasets/r/4806ff8c-1038-41c3-8547-298980172e09"
PLF2025_DEPENSES_URL = "https://www.data.gouv.fr/fr/datasets/r/b7da87c8-e4e3-4914-8a69-9014f95136d9"
PLF2024_RECETTES_URL = "https://www.data.gouv.fr/fr/datasets/r/8cfff293-a2f3-4885-8262-81533fd71908"
PLF2019_RECETTES_URL = "https://www.data.gouv.fr/fr/datasets/r/a9ee1c49-0e95-4b47-afff-9c80346d853b"
PLF2019_MISSION_URL = "https://www.data.gouv.fr/fr/datasets/r/8002479f-6fb4-4f98-a571-6946ed21eb3f"

OUTPUT_DIR = Path(__file__).parent.parent / "output"
COLORS = {
    "France": "#0055A4",
    "EU_avg": "#E63946",
    "accent": "#FF6B6B",
    "bg": "#F8F9FA",
}


def fetch_csv(url: str, encoding: str = "utf-8") -> pd.DataFrame:
    """Download CSV from data.gouv.fr and return DataFrame."""
    with urllib.request.urlopen(url, timeout=30) as r:
        content = r.read().decode(encoding, errors="replace")
    return pd.read_csv(io.StringIO(content), sep=";" if ";" in content[:500] else ",")


def plot_france_vs_europe_spending(df: pd.DataFrame, out_path: Path) -> None:
    """Stacked bar: France vs EU average by spending category."""
    fr = df[df["geo"] == "FR"].copy()
    if fr.empty:
        fr = df[df["Pays"] == "France"].copy()
    if fr.empty:
        print("No France data in skyline")
        return

    # Aggregate by Dépense (category)
    cat = fr.groupby("Dépense", as_index=False)["Valeur"].sum()
    cat = cat.sort_values("Valeur", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 7))
    bars = ax.barh(cat["Dépense"], cat["Valeur"], color=COLORS["France"], alpha=0.85, edgecolor="white", linewidth=0.5)
    ax.set_xlabel("% du PIB potentiel")
    ax.set_title("Dépenses publiques en France par fonction (% PIB)")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    fig.savefig(out_path / "1_france_spending_by_category.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path / '1_france_spending_by_category.png'}")


def plot_europe_comparison_heatmap(df: pd.DataFrame, out_path: Path) -> None:
    """Heatmap: countries × spending categories."""
    pivot = df.pivot_table(index="Pays", columns="Dépense", values="Valeur", aggfunc="sum")
    pivot = pivot.fillna(0)

    fig, ax = plt.subplots(figsize=(14, 10))
    im = ax.imshow(pivot.values, cmap="YlOrRd", aspect="auto", vmin=0, vmax=25)
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=9)
    ax.set_title("Dépenses publiques par pays et fonction (% PIB)")
    plt.colorbar(im, ax=ax, label="% PIB")
    plt.tight_layout()
    fig.savefig(out_path / "2_europe_heatmap.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path / '2_europe_heatmap.png'}")


def plot_france_vs_selected(df: pd.DataFrame, out_path: Path, countries: list = None) -> None:
    """Grouped bar: France vs DE, IT, ES for main categories."""
    countries = countries or ["France", "Allemagne", "Italie", "Espagne"]
    sub = df[df["Pays"].isin(countries)].copy()
    if sub.empty:
        return

    # Top-level categories only (G1, G2, G3, G4, G5)
    top_codes = ["G1", "G2", "G3", "G4", "G5"]
    sub = sub[sub["Code"].isin(top_codes)]
    cat_names = {
        "G1": "Redistribution",
        "G2": "Services sociaux",
        "G3": "Services généraux",
        "G4": "Soutien économie",
        "G5": "Charge dette",
    }
    sub["Cat"] = sub["Code"].map(cat_names)

    pivot = sub.pivot_table(index="Cat", columns="Pays", values="Valeur", aggfunc="sum")
    order = [cat_names[c] for c in top_codes if c in sub["Code"].values]
    if not order:
        return
    pivot = pivot.reindex([c for c in order if c in pivot.index]).dropna(how="all")
    if pivot.empty:
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    pivot.plot(kind="bar", ax=ax, width=0.8, colormap="Set2")
    ax.set_ylabel("% PIB")
    ax.set_title("Comparaison des dépenses publiques – France vs voisins européens")
    ax.legend(title="Pays", bbox_to_anchor=(1.02, 1), loc="upper left")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    fig.savefig(out_path / "3_france_vs_europe_bars.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path / '3_france_vs_europe_bars.png'}")


def plot_budget_by_mission(df: pd.DataFrame, out_path: Path, top_n: int = 15) -> None:
    """Horizontal bar: top missions by budget (CP)."""
    # Detect column names (encoding may vary; PLF 2025 uses "credit de paiement", "libelle mission")
    cp_col = None
    mission_col = None
    for c in df.columns:
        c_lower = c.lower().strip()
        if "credit" in c_lower and "paiement" in c_lower:
            cp_col = c
        elif "crédit" in c_lower or (cp_col is None and "cp" in c_lower):
            cp_col = cp_col or c
        if "libelle mission" in c_lower or "mission" in c_lower:
            mission_col = c

    if cp_col is None:
        cand = [c for c in df.columns if "PLF" in c or "2019" in c or "2025" in c or "paiement" in c.lower()]
        cp_col = cand[-1] if cand else df.columns[-1]
    if mission_col is None:
        mission_col = [c for c in df.columns if "mission" in c.lower()][0] if any("mission" in c.lower() for c in df.columns) else df.columns[5]

    # Clean numeric column
    df_clean = df.copy()
    df_clean["_cp"] = pd.to_numeric(
        df_clean[cp_col].astype(str).str.replace(" ", "").str.replace("\xa0", ""),
        errors="coerce",
    )
    df_clean = df_clean.dropna(subset=["_cp"])
    by_mission = df_clean.groupby(mission_col, as_index=False)["_cp"].sum()
    by_mission = by_mission.nlargest(top_n, "_cp")
    by_mission["_cp_M"] = by_mission["_cp"] / 1e6

    fig, ax = plt.subplots(figsize=(10, 8))
    bars = ax.barh(
        range(len(by_mission)),
        by_mission["_cp_M"],
        color=COLORS["France"],
        alpha=0.85,
        edgecolor="white",
    )
    ax.set_yticks(range(len(by_mission)))
    ax.set_yticklabels(by_mission[mission_col].str[:45], fontsize=9)
    ax.set_xlabel("Crédits de paiement (millions €)")
    ax.set_title("Budget de l'État – Top missions par crédits de paiement")
    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    fig.savefig(out_path / "4_budget_top_missions.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path / '4_budget_top_missions.png'}")


def plot_tax_revenue_pie(df: pd.DataFrame, out_path: Path, top_n: int = 10) -> None:
    """Pie chart: share of tax revenue by type."""
    # Find columns
    label_col = None
    value_col = None
    for c in df.columns:
        if "recette" in c.lower() or "intitul" in c.lower():
            label_col = c
        if "euro" in c.lower() or "évaluation" in c.lower() or "2019" in c or "2024" in c:
            value_col = c

    if label_col is None:
        label_col = df.columns[1]
    if value_col is None:
        value_col = [c for c in df.columns if df[c].dtype in ["float64", "int64"]][0]

    df_clean = df.copy()
    df_clean["_val"] = pd.to_numeric(
        df_clean[value_col].astype(str).str.replace(" ", "").str.replace("\xa0", ""),
        errors="coerce",
    )
    df_clean = df_clean.dropna(subset=["_val"])
    df_clean = df_clean[df_clean["_val"] > 0]
    # Filter out section headers (empty or very long)
    df_clean = df_clean[df_clean[label_col].astype(str).str.len() < 80]
    top = df_clean.nlargest(top_n, "_val")
    other = df_clean.nsmallest(len(df_clean) - top_n, "_val")["_val"].sum()
    if other > 0:
        top = pd.concat([top, pd.DataFrame([{label_col: "Autres", "_val": other}])], ignore_index=True)

    fig, ax = plt.subplots(figsize=(10, 8))
    colors = plt.cm.Set3(range(len(top)))
    wedges, texts, autotexts = ax.pie(
        top["_val"],
        labels=top[label_col].str[:35],
        autopct="%1.1f%%",
        startangle=90,
        colors=colors,
        pctdistance=0.75,
    )
    for t in texts:
        t.set_fontsize(8)
    ax.set_title("Recettes fiscales de l'État – Répartition par type d'impôt")
    plt.tight_layout()
    fig.savefig(out_path / "5_tax_revenue_pie.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path / '5_tax_revenue_pie.png'}")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Fetching data from data.gouv.fr...")

    # 1. Skyline (Europe)
    try:
        skyline = fetch_csv(SKYLINE_URL, encoding="utf-8")
        print(f"Skyline: {len(skyline)} rows")
        plot_france_vs_europe_spending(skyline, OUTPUT_DIR)
        plot_europe_comparison_heatmap(skyline, OUTPUT_DIR)
        plot_france_vs_selected(skyline, OUTPUT_DIR)
    except Exception as e:
        print(f"Skyline error: {e}")

    # 2. PLF budget by mission (try 2025 first, fallback 2019)
    for url, label in [(PLF2025_DEPENSES_URL, "2025"), (PLF2019_MISSION_URL, "2019")]:
        try:
            budget = fetch_csv(url, encoding="utf-8")
            print(f"Budget {label}: {len(budget)} rows, cols: {list(budget.columns)[:5]}...")
            plot_budget_by_mission(budget, OUTPUT_DIR)
            break
        except Exception as e:
            print(f"Budget {label} error: {e}")

    # 3. Tax revenue (try 2024 first, fallback 2019)
    for url, label in [(PLF2024_RECETTES_URL, "2024"), (PLF2019_RECETTES_URL, "2019")]:
        try:
            recettes = fetch_csv(url, encoding="utf-8")
            print(f"Recettes {label}: {len(recettes)} rows")
            plot_tax_revenue_pie(recettes, OUTPUT_DIR)
            break
        except Exception as e:
            print(f"Recettes {label} error: {e}")

    print(f"\nPlots saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
