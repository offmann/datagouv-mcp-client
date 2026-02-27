# Public Money Spending – Data Inventory (data.gouv.fr)

This document inventories datasets on **data.gouv.fr** related to public spending (taxes, budget, public spending) and suggests visualization approaches.

---

## 1. European Public Spending Comparison (Skyline)

**Dataset:** [Comparaison des depenses publiques en France et en Europe](https://www.data.gouv.fr/datasets/6930d1070f79645f340f7ed9)  
**Organization:** Ministry of Solidarity and Health  
**Dataset ID:** `6930d1070f79645f340f7ed9`

### Resources
| Resource | Format | ID |
|----------|--------|-----|
| skyline.csv | CSV | `4806ff8c-1038-41c3-8547-298980172e09` |
| skyline.json | JSON | `bb937429-bf4f-46ff-8106-e62bbbdfb3ec` |

### Data structure (skyline.csv)
| Column | Description |
|--------|-------------|
| geo | Country code (FR, DE, IT, etc.) |
| Pays | Country name |
| Annee | Year |
| Code | Function code (G1, G2, G21, etc.) |
| Depense | Spending category (e.g. "Sante", "Education et recherche") |
| Valeur | % of GDP |
| Moy11 | European average |
| Ecart | Difference from average |

### Spending categories (CFAP)
- **G1** - Monetary redistribution benefits (retirement, social support)
- **G2** - Social and cultural services provision
- **G21** - Health
- **G22** - Education and research
- **G23** - Leisure and cultural activities
- **G24** - Personal support
- **G3** - General public services provision
- **G31** - Defense, police, justice
- **G32** - General administration
- **G4** - Economic support
- **G41** - Subsidies and transfers
- **G42** – Investissement
- **G5** – Charge de la dette

### Suggested visualizations
- **Stacked bar chart** – France vs EU average by spending category
- **Heatmap** – Countries × categories (% GDP)
- **Radar chart** – France vs 2–3 other countries
- **Horizontal bar** – Top spending categories by country

---

## 2. French State Budget - Spending by Mission (PLF)

**Dataset:** [PLF 2025 - Depenses 2025 selon destination](https://www.data.gouv.fr/datasets/6709bd95daeddce062e00b23)  
**Organization:** Ministry of Economy and Finance  
**Dataset ID:** `6709bd95daeddce062e00b23`

### Resources
| Resource | Format | ID |
|----------|--------|-----|
| plf25-depenses-2025-selon-destination.csv | CSV | `b7da87c8-e4e3-4914-8a69-9014f95136d9` |

### Data structure
- **Mission** - Policy area (e.g. "Education", "Defense")
- **Programme** – Sub-program
- **Action** – Action
- **AE** - Commitment appropriations (€)
- **CP** - Payment appropriations (€)
- **Ministere** - Ministry

### Suggested visualizations
- **Treemap** – Budget by mission (and optionally programme)
- **Sunburst** – Mission → Programme → Action
- **Horizontal bar** – Top 15 missions by CP
- **Pie chart** – Share of budget by mission

---

## 3. French State Budget - Tax Revenue

**Dataset:** [PLF 2024 - Recettes du budget general](https://www.data.gouv.fr/datasets/655d451f5a475da831a6435c)  
**Organization:** Ministry of Economy and Finance  
**Dataset ID:** `655d451f5a475da831a6435c`

### Resources
| Resource | Format | ID |
|----------|--------|-----|
| plf-2024-recettes-du-budget-general.csv | CSV | `8cfff293-a2f3-4885-8262-81533fd71908` |

### Data structure (PLF 2019 equivalent)
- **Intitule de la recette** - Tax type (IR, IS, TVA, TICPE, etc.)
- **Evaluation (€)** - Estimated revenue

### Main tax categories
- Income tax (IR)
- Corporate income tax (IS)
- Value-added tax (TVA)
- Domestic tax on energy products (TICPE)
- Enregistrement, timbre, autres taxes indirectes

### Suggested visualizations
- **Pie chart** – Share of tax revenue by type
- **Horizontal bar** – Top 10 tax sources
- **Waterfall** – Contribution of each tax to total

---

## 4. Other relevant datasets

| Dataset | ID | Description |
|---------|-----|-------------|
| Public administration spending by function | 5369928ea3a729239d203f64 | CFAP spending (XLS) |
| PLF 2019 general budget by mission | 5bbf6ee68b4c416d795e9cab | Full PLF 2019 (missions, revenues, etc.) |
| Operating spending (local authorities) | Various | City-level spending (Agen, Issy, etc.) |

---

## Resource URLs (direct download)

```
# Skyline (Europe)
https://www.data.gouv.fr/fr/datasets/r/4806ff8c-1038-41c3-8547-298980172e09

# PLF 2025 spending
https://www.data.gouv.fr/fr/datasets/r/b7da87c8-e4e3-4914-8a69-9014f95136d9

# PLF 2024 tax revenue
https://www.data.gouv.fr/fr/datasets/r/8cfff293-a2f3-4885-8262-81533fd71908

# PLF 2019 tax revenue (backup)
https://www.data.gouv.fr/fr/datasets/r/a9ee1c49-0e95-4b47-afff-9c80346d853b

# PLF 2019 budget by mission
https://www.data.gouv.fr/fr/datasets/r/8002479f-6fb4-4f98-a571-6946ed21eb3f
```

---

## Summary

| Data type | Best dataset | Best plot types |
|----------|--------------|-----------------|
| **European comparison** | Skyline | Stacked bar, heatmap, radar |
| **French budget (spending)** | PLF 2025 spending | Treemap, bar, pie |
| **French tax revenue** | PLF 2024 tax revenue | Pie, horizontal bar |
