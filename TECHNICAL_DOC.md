# Technical Document — CAExploratory Data Analysis (Superstore Sales EDA)

**Scope:** Technical / architectural documentation of the `CodeAlpha_EDA_SuperstoreSales` repository.
**Produced by:** static analysis of the committed source + runtime verification against the checked-out tree.
**Working tree:** `C:\Users\nayak\Desktop\Intership Projects\CAExploratory Data Analysis`
**Branch:** `main` (3 commits; diverged from `origin/main` — 2 commits ahead, 3 behind)
**Origin:** `https://github.com/nayaksuvamsuryakanta-a11y/CodeAlpha_EDA_SuperstoreSales.git`

> **Verification log.** A subset of the facts below were confirmed by executing the code, not just
> reading it: the notebook was run end-to-end through `nbconvert --execute` (0 cell errors, 33 code
> cells), and the headline analytics were recomputed independently to check the notebook's own claims
> against ground truth. Discrepancies found this way are flagged ⚠️ in §13.

---

## 1. Project overview

| Attribute | Value |
|---|---|
| **Purpose** | Exploratory data analysis of a retail superstore order dataset, framed as *CodeAlpha Internship — Task 2: Exploratory Data Analysis*. The deliverable is a reproducible notebook that answers five business questions and produces a figure deck. |
| **Main features** | Synthetic data generation replicating the Tableau Sample Superstore schema; data loading with a self-diagnosing loader; univariate / bivariate / time-series analysis; statistical hypothesis testing (5 tests); 16 publication-grade figures; an executive summary with recommendations. |
| **Target users** | The internship author / reviewer; anyone evaluating an EDA workflow on the Superstore dataset. |
| **Delivery shape** | Single Jupyter notebook (`superstore_eda.ipynb`) + a deterministic data generator (`generate_superstore.py`) + a loose `testing.py` smoke check. |
| **Tech stack** | Python 3.14, pandas 3.0.6, numpy 2.5.3, scipy 1.18.1, statsmodels 0.15.0, matplotlib 3.11.2, seaborn 0.13.2, ipykernel 7.3.0. All analysis is local/offline — no server, no database, no network calls. |

### 1.1 What the notebook does, in one pass

1. Loads `Sample - Superstore.csv` (falls back to an `.xlsx`, errors with a directory listing if neither exists).
2. Parses `Order Date` / `Ship Date`, derives `Order Year/Month/Quarter`, `Ship Days`, `is_loss`, `Profit Margin`, `Discount Band`.
3. Reports structure, missingness, duplicates, IQR outliers.
4. Plots distributions, boxplots, categorical counts, monthly/quarterly trends, correlation heatmap, discount-vs-profit regression, sub-category profit bars, ship-mode boxplots, a pairplot, segment×region heatmaps and bars, margin ranking.
5. Runs five hypothesis tests (Pearson/OLS, one-way ANOVA + Tukey HSD, Welch's t-test, chi-square, point-biserial with bootstrap CI).
6. Prints an executive summary and a recommendations table.

---

## 2. Architecture

This is a **single-process, script-style data-analysis pipeline**, not a service. There is no
client/server split, no API layer, and no persistent store. Data flows linearly:

```
┌─────────────────────┐      ┌──────────────────────────────────────┐
│ generate_superstore.py│────▶│  Sample - Superstore.csv              │
│ (deterministic,     │      │  (21 cols × 9,994 rows, latin-1)      │
│  SEED=42, N=9994)   │      └──────────────┬───────────────────────┘
└─────────────────────┘                     │
                                            ▼
                              ┌─────────────────────────────┐
                              │ superstore_eda.ipynb        │
                              │  ├─ load_superstore()       │
                              │  ├─ date parsing + derives  │
                              │  ├─ quality report          │
                              │  ├─ visualisation blocks    │
                              │  └─ 5 hypothesis tests      │
                              └───────────────┬─────────────┘
                                              │
                 ┌────────────────────────────┼────────────────────────────┐
                 ▼                            ▼                            ▼
        ┌───────────────┐         ┌───────────────────┐          ┌─────────────────┐
        │ fig_*.png     │         │ stdout / notebook │          │ testing.py      │
        │ (16 figures)  │         │ cell outputs      │          │ (3 ad-hoc Qs)   │
        └───────────────┘         └───────────────────┘          └─────────────────┘
```

### Component responsibilities

| Component | File(s) | Responsibility |
|---|---|---|
| Synthetic data generator | `generate_superstore.py` | Emits a CSV whose schema, value ranges and marginal distributions mirror the public Tableau Sample Superstore dataset. Deterministic via `SEED = 42`. |
| EDA notebook | `superstore_eda.ipynb` | The entire analysis: load → clean → explore → visualise → test → report. Kernel declared as `python3`. |
| Loader | `superstore_eda.ipynb` cell `load-data` | `load_superstore()` — tries CSV, then XLSX, else raises a `FileNotFoundError` containing the cwd, the names searched, other CSVs/XLSXs present, and two fix options. |
| Smoke check | `testing.py` | Three unasserted `groupby` aggregations sold as "Q1 / Q2". |
| Outputs | `fig_*.png` (16 files) | Charts saved by the notebook at `dpi=150` (`fig_pairplot.png` at `dpi=120`). |

### Data flow within the notebook (cell order)

```
imports-cell (1)
   → load-data (2)                parse-dates (3)
        → dataset_overview (4)
              → missing_values_report (5)
                    → duplicates (6)
                          → desc-stats (7)
                                → cat-cardinality (8)
                                      → outlier-scan (9)
                                            → [sections 4..9: plotting + tests]
                                                  → exec-stats (31) → summary-chart (32)
                                                                              → final-cell (33)
```

---

## 3. Folder and file structure

```
CAExploratory Data Analysis/
├── .git/                         # git repo (main, 3 commits, origin wired to GitHub)
├── .ipynb_checkpoints/
│   └── superstore_eda-checkpoint.ipynb   # Jupyter auto-checkpoint from an early state (~4% of main notebook size)
├── fig_boxplots.png               # Boxplots — Outlier Visibility
├── fig_categorical.png            # Univariate — Categorical Variables
├── fig_chi2_heatmap.png           # Contingency Table: Segment x Ship Mode
├── fig_correlation.png            # Pearson Correlation Matrix
├── fig_discount_profit.png        # Discount vs Profit (+ OLS line + 95% CI band)
├── fig_distributions.png          # Distributions of Core Numeric Variables
├── fig_margin_ranking.png         # Sub-Category Profit Margin Ranking
├── fig_monthly_trend.png          # Monthly Sales & Profit Trends (2014-2017)
├── fig_pairplot.png               # Key Numerics by Category (n=500 sample)
├── fig_region_segment.png         # Total Profit by Region and Customer Segment
├── fig_seasonality.png            # Quarterly Sales by Year + Seasonality Index
├── fig_seg_region_heatmap.png     # Profit and Avg Margin by Segment x Region
├── fig_ship_mode.png              # Days to Ship by Shipping Mode
├── fig_subcat_profit.png          # Total Profit by Sub-Category
├── fig_summary.png                # Executive Summary — Key Profit Drivers
├── fig_tukey.png                  # Tukey HSD — 95% CIs for Region Mean Profits
├── generate_superstore.py         # ~285 lines; deterministic synthetic dataset generator
├── Sample - Superstore.csv        # 2,079,966 B — 9,994 rows × 21 cols, latin-1  (generated)
├── Sample - Superstore2.csv       # BYTE-IDENTICAL duplicate of Sample - Superstore.csv (dead weight)
├── superstore_eda.ipynb           # 33 code + 45 markdown cells; kernel "python3"
└── testing.py                     # 6 lines; three unasserted groupby aggregations
```

### Important files

| File | Lines / size | Role |
|---|---|---|
| `superstore_eda.ipynb` | 1,354,657 B; 78 cells | Primary deliverable. Contains loader, analysis, 5 tests, narrative. |
| `generate_superstore.py` | ~285 lines | Reproduces the dataset without downloading it. `SEED = 42`, `N = 9994`. |
| `Sample - Superstore.csv` | 9,994 rows × 21 cols | The analysis input. **Generated, not the real Kaggle file.** |
| `testing.py` | 6 lines | Ad-hoc verification; no assertions, no framework. |
| `Sample - Superstore2.csv` | identical to the above | Duplicate — see §13.3. |

---

## 4. Libraries and dependencies

**There is no dependency manifest in the repo** — no `requirements.txt`, `pyproject.toml`,
`setup.cfg`, `Pipfile`, `environment.yml`, `poetry.lock`, `uv.lock`, `Pipfile.lock`, or
`setup.py` (§9). Versions below were obtained by importing each module in the interpreters present
on the machine.

### 4.1 Runtime dependencies (analysis stack)

| Library | Version | Runtime | Used where / for what | Files |
|---|---|---|---|---|
| `pandas` | **3.0.6** | runtime | DataFrame I/O (`read_csv`, `to_csv`), grouping/aggregation, `pd.cut` binning, datetime parsing, `.describe()`, Styler. | `generate_superstore.py`, `superstore_eda.ipynb`, `testing.py` |
| `numpy` | **2.5.3** | runtime | `np.random` sampling, `np.array` weight normalisation, `np.random.normal` noise, numeric arrays. | `generate_superstore.py`, `superstore_eda.ipynb` |
| `scipy` | **1.18.1** | runtime | All inferential statistics: `stats.linregress`, `stats.f_oneway`, `stats.ttest_ind`, `stats.chi2_contingency`, `stats.pointbiserialr`, `stats.t`, `t_dist`, bootstrap. | `superstore_eda.ipynb` |
| `statsmodels` | **0.15.0** | runtime | `pairwise_tukeyhsd` (ANOVA post-hoc). | `superstore_eda.ipynb` |
| `matplotlib` | **3.11.2** | runtime | All 16 figures (`plt.subplots`, `savefig`, `FuncFormatter`, `mtick`, `mpatches`, `Normalize`). | `superstore_eda.ipynb` |
| `seaborn` | **0.13.2** | runtime | `sns.histplot`, `sns.boxplot`, `sns.countplot`, `sns.heatmap`, `sns.pairplot`, `sns.set_theme`, `sns.color_palette`. | `superstore_eda.ipynb` |
| `ipykernel` | **7.3.0** | runtime | Notebook execution kernel. | `superstore_eda.ipynb` (kernel spec `python3`) |

### 4.2 Tooling / dev dependencies

| Tool | Version | Role | Declared in repo? |
|---|---|---|---|
| `nbconvert` | **7.17.1** | Notebook execution / conversion. Used externally (not referenced by repo code) to verify this document. | **No** |
| `papermill` | not installed | Parameterised notebook execution. | **No — not present** |

### 4.3 Interpreters observed

| Interpreter | pandas | numpy | scipy | statsmodels | matplotlib | seaborn | ipykernel |
|---|---|---|---|---|---|---|---|
| `Python314` (default `python`, 3.14.0) | 3.0.6 | 2.5.3 | 1.18.1 | 0.15.0 | 3.11.2 | 0.13.2 | 7.3.0 |
| `Python312` (3.12.10) | **missing** | 1.26.4 | 1.17.1 | **missing** | 3.11.2 | **missing** | **missing** |

> ⚠️ **Environment risk.** The project has no pinned manifest. The default `python` on this machine
> works, but `Python312` — a plausible alternate interpreter — cannot run a single line of the
> analysis. A developer hitting `python superstore_eda.ipynb` on a fresh machine gets
> `ModuleNotFoundError` with no guidance from the repo.

### 4.4 Notes on duplication, staleness, unused packages

- **No unused runtime imports** — every imported name is referenced.
- **No duplicate packages** — but `Sample - Superstore2.csv` is a byte-identical duplicate of
  `Sample - Superstore.csv` (same SHA-256 prefix `655c80981cf2e7c6`, same 2,079,966 B). Dead weight.
- **pandas 3.0 note:** `superstore_eda.ipynb` uses `pd.set_option('display.float_format',
  '{:,.2f}'.format)`, which passed a callable and ran without deprecation error under pandas 3.0.6.
  It is worth watching: the string-formatter form of this option was deprecated in pandas 2.x, and
  a future pandas may drop the callable path too. The same notebook also calls `df.isnull()`, which
  pandas 3.x still supports in favour of `isna()`.
- **Encoding inconsistency:** `generate_superstore.py` writes `encoding='latin-1'` while
  `testing.py` reads `encoding="windows-1252"`. Harmless here (all generated content is ASCII), but
  a latent mismatch on non-ASCII data.

---

## 5. APIs used (external)

**None.** The codebase makes no HTTP requests, imports no HTTP client (`requests`, `httpx`,
`urllib`), and contains no base URLs, endpoints, auth tokens, API keys, or retry logic.

The only external *reference* is a URL mentioned in prose, inside `superstore_eda.ipynb`
(cell `load-header`, markdown):

- `https://www.kaggle.com/datasets/vivek468/superstore-dataset-final` — cited as "Option A (real
  data)". It is **never fetched by code**; the notebook ships the synthetic CSV instead.
- Kaggle datasets normally require authentication, so this link would not be machine-retrievable
  as-is without a Kaggle session cookie / API token.

**Everything the project needs is local.**

---

## 6. APIs exposed (internal)

**None.** There is no web server, no REST/GraphQL/gRPC endpoint, no middleware, and no route table.
The project is not a service.

The only reusable callable exposed by the code is `load_superstore(csv_path, xlsx_path)` in
`superstore_eda.ipynb` (cell `load-data`), which is a plain Python function, not an HTTP endpoint:

| Attribute | Value |
|---|---|
| Name | `load_superstore` |
| Signature | `load_superstore(csv_path='Sample - Superstore.csv', xlsx_path='Sample - Superstore.xlsx')` |
| Purpose | Load the Superstore dataset from CSV or XLSX, with a directory-diagnosing error. |
| Search order | 1. `cwd / csv_path`, 2. `cwd / xlsx_path` (falls back from the `Orders` sheet to the first sheet). |
| Returns | `pd.DataFrame` |
| Raises | `FileNotFoundError` whose message includes `cwd`, the two filenames searched, any `.csv/.xlsx/.xls` files present, and step-by-step fix instructions (`py generate_superstore.py` or download from Kaggle). |

---

## 7. Data layer

There is **no database, no ORM, no migration system, no cache, and no file-storage service**. Data is
a single flat CSV read into memory.

### 7.1 Source schema — `Sample - Superstore.csv` (21 columns)

| # | Column | Type (as stored) | Notes |
|---|---|---|---|
| 0 | `Row ID` | int | 1..9,994 |
| 1 | `Order ID` | str | `CA-<YYYY>-<6-digit>` — e.g. `CA-2016-000001` |
| 2 | `Order Date` | str | **`DD/MM/YYYY`** — e.g. `25/06/2016` |
| 3 | `Ship Date` | str | `DD/MM/YYYY` |
| 4 | `Ship Mode` | str | `Standard Class`, `Second Class`, `First Class`, `Same Day` |
| 5 | `Customer ID` | str | `C-<5-digit>` — 800 distinct values |
| 6 | `Customer Name` | str | 50-name pool, mapped from customer id |
| 7 | `Segment` | str | `Consumer`, `Corporate`, `Home Office` |
| 8 | `Country` | str | `United States` (constant) |
| 9 | `City` | str | ~70 cities |
| 10 | `State` | str | 28 states |
| 11 | `Postal Code` | int | 5-digit string read as int (leading zeros lost) |
| 12 | `Region` | str | `West`, `East`, `Central`, `South` |
| 13 | `Product ID` | str | `P-<subcat prefix>-<3-digit>` — e.g. `P-BIN-068` |
| 14 | `Category` | str | `Furniture`, `Office Supplies`, `Technology` |
| 15 | `Sub-Category` | str | 17 sub-categories |
| 16 | `Product Name` | str | 33-name pool |
| 17 | `Sales` | float | `unit_price * quantity` |
| 18 | `Quantity` | int | 1..14 |
| 19 | `Discount` | float | 0.0 .. 0.8 in 0.1 steps |
| 20 | `Profit` | float | can be negative |

CSV encoding: `latin-1` (writer, `generate_superstore.py:195`).

### 7.2 Derived columns created by the notebook (cell `parse-dates`, 3)

| Column | Type | Definition |
|---|---|---|
| `Order Year` | int32 | `Order Date.dt.year` |
| `Order Month` | int32 | `Order Date.dt.month` |
| `Order Quarter` | int32 | `Order Date.dt.quarter` |
| `Ship Days` | float64 | `(Ship Date - Order Date).dt.days` |
| `is_loss` | int64 | `(Profit < 0).astype(int)` |
| `Profit Margin` | float64 | `Profit / Sales` |
| `Discount Band` | category | `pd.cut` bins `[-0.01, 0, 0.2, 0.4, 0.6, 1.0]` → `['0%', '1-20%', '21-40%', '41-60%', '>60%']` |

### 7.3 Data quality (as reported by the notebook itself, §3)

| Check | Result |
|---|---|
| Shape | 9,994 rows × 28 columns (21 original + 7 derived) |
| Memory | 3,381.9 KB |
| Missing values | `Ship Date` 6,089 (60.93%), `Ship Days` 6,089 (60.93%) — **an artefact of a parsing bug, see §13.1** |
| Exact duplicate rows | 0 |
| Duplicate `Order ID` + `Product ID` | 0 |
| IQR outliers | `Sales` 1,349 (13.50%), `Discount` 2,237 (22.38%), `Profit` 2,852 (28.54%), `Quantity` 222 (2.22%), `Ship Days` 0 |
| Cardinality | `Country`=1, `Segment`=3, `Region`=4, `Ship Mode`=4, `Category`=3, `Sub-Category`=17 |

### 7.4 Ground-truth recomputation (verified independently)

| Metric | Value |
|---|---|
| Total revenue | $23,188,571 |
| Total profit | $492,716 |
| Overall margin | 2.1 % |
| Loss-making orders | 31.8 % (3,182 of 9,994) |
| Unique customers | 800 |
| Unique orders | 9,994 |
| Date range | 01/01/2014 – 31/12/2017 |
| Discount values present | `[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]` |
| Orders by category | Office Supplies 5,983 (59.9 %), Furniture 2,120 (21.2 %), Technology 1,891 (18.9 %) |
| Profit by category | Technology +$2,298,007; Office Supplies −$148,007; Furniture −$1,657,285 |
| Orders by ship mode | Standard Class 5,947 (59.5 %), Second Class 1,891 (18.9 %), First Class 1,501 (15.0 %), Same Day 655 (6.6 %) |
| Mean profit by segment | Consumer $24.81 (n=4,994), Corporate $41.37 (n=3,074), Home Office $125.48 (n=1,926) |
| Mean profit by region | East $83.21, Central $46.58, South $43.76, West $23.49 |
| Q4 share of annual sales | 36.52 % |

---

## 8. Core flows

### 8.1 Dataset generation flow — `generate_superstore.py`

Run: `py generate_superstore.py` (writes `Sample - Superstore.csv` to the cwd).

1. **Seed** (`lines ~15-17`): `random.seed(42)`, `np.random.seed(42)`, `N = 9994`.
2. **Define reference tables** (`lines ~20-115`): regions + weights, states per region, cities per state, segments, ship modes + day lags, the `CATEGORIES` dict (17 sub-categories, each with `price_range`, `base_margin`, `discount_freq`).
3. **Build sub-category sampling weights** (`lines ~117-125`): category weights `Furniture 0.21 / Office Supplies 0.60 / Technology 0.19`, flattened and normalised.
4. **Customer pool** (`lines ~135-152`): 800 customer IDs `C-00001..C-00800`, each assigned a segment; names drawn from a 50-name pool via `int(cid.split('-')[1]) % 50`.
5. **Product ID pool** (`lines ~154-166`): 10 IDs per sub-category, keyed `(cat, subcat, j)`.
6. **Row loop** (`for _ in range(N)`, `lines ~187-220`): for each row pick customer → region/state/city/postal → product → order date (`random_date()`, Q4-weighted) → ship mode → lag → dates → price/quantity/sales → discount → profit → order id.
7. **Profit model** (the critical line, `line ~215`):
   ```python
   effective_margin = bm - discount * 1.8 + np.random.normal(0, 0.04)
   profit = round(sales * effective_margin, 2)
   ```
   The `* 1.8` multiplier is what makes discounts punitive — see §13.5.
8. **Persist** (`line ~195`): `df.to_csv(out_path, index=False, encoding='latin-1')`.

### 8.2 EDA flow — `superstore_eda.ipynb`

Linear cell sequence (§2). Highlights:

- **Load** (`load-data`, 2): `load_superstore()` → CSV → XLSX → actionable `FileNotFoundError`.
- **Parse** (`parse-dates`, 3): `_is_string_dtype()` + `_detect_dayfirst()` → `pd.to_datetime(..., dayfirst=<detected>, errors='coerce')` → derives time features + business flags.
- **Quality** (4–9): `dataset_overview()`, `missing_values_report()`, `duplicated()`, `describe().T.style`, cardinality loop, `iqr_outlier_count()`.
- **Visualisation** (10–23): every figure is saved via `plt.savefig('fig_<name>.png', dpi=150, bbox_inches='tight')` then `plt.show()`.
- **Hypothesis tests** (24–30): `report_test()` prints a uniform block (test name, statistic, p-value, conclusion at `alpha=0.05`, extras). Tests: OLS/Pearson (H1), ANOVA + Tukey HSD (H2), Welch's t-test + Cohen's d (H3), chi-square + Cramér's V (H4), point-biserial + 1,000-iteration bootstrap CI (H5).
- **Summary** (31–33): executive stats, 3-panel summary figure, globbed figure inventory.

### 8.3 Background jobs

**None.** No schedulers, workers, cron entries, or async tasks exist in the repo.

---

## 9. Configuration and environment

### 9.1 Environment variables

**None are read or documented.** The repo contains no `.env`, `.env.example`, or `os.environ`
lookups. Every path is relative to `pathlib.Path.cwd()`.

### 9.2 Config files

| File | Exists? | Purpose |
|---|---|---|
| `requirements.txt` | **Not found in code** | — |
| `pyproject.toml` | **Not found in code** | — |
| `setup.cfg` / `setup.py` | **Not found in code** | — |
| `Pipfile` / `Pipfile.lock` | **Not found in code** | — |
| `environment.yml` | **Not found in code** | — |
| `Dockerfile` / `docker-compose.yml` | **Not found in code** | — |
| `.github/workflows/*` (CI) | **Not found in code** | — |
| `.gitignore` | **Not found in code** | — |
| `README.md` | **Not found in code** | — |
| `pytest.ini` / `tox.ini` / `.pre-commit-config.yaml` | **Not found in code** | — |
| `.qwen/` config | **Not found in code** | — |

### 9.3 Hardcoded configuration (from the source)

| Constant | Value | Where | Meaning |
|---|---|---|---|
| `SEED` | `42` | `generate_superstore.py:16`, `superstore_eda.ipynb:imports-cell` | RNG seed for reproducibility |
| `N` | `9994` | `generate_superstore.py:18` | Row count matching the real dataset |
| `ALPHA` | `0.05` | `superstore_eda.ipynb:imports-cell` | Significance level for all hypothesis tests |
| `FIGSIZE` | `(12, 5)` | `imports-cell` | Default figure size (not used by all plots) |
| `REGION_WEIGHTS` | `[0.32, 0.29, 0.21, 0.18]` | `generate_superstore.py` | West/East/Central/South order share |
| `SEGMENT_WEIGHTS` | `[0.52, 0.30, 0.18]` | `generate_superstore.py` | Consumer/Corporate/Home Office share |
| `SHIP_MODE_WEIGHTS` | `[0.59, 0.19, 0.15, 0.07]` | `generate_superstore.py` | Ship-mode share |
| `category weights` | Furniture 0.21 / Office Supplies 0.60 / Technology 0.19 | `generate_superstore.py` | Sub-category sampling |
| `DISCOUNT_VALUES` | 16 values, 0.0×4, then 0.1..0.8 | `generate_superstore.py` | Discrete discount grid |

### 9.4 Feature flags

**None in code.**

---

## 10. Setup and run guide

Commands are taken from the project's own scripts (`generate_superstore.py` docstring and the
notebook's `load-header` markdown).

### 10.1 Prerequisites

- Python 3.12+ (the machine's default `python` is 3.14.0, which has all deps; 3.12.10 does not — §4.3).
- Packages: `pandas`, `numpy`, `scipy`, `statsmodels`, `matplotlib`, `seaborn`, `ipykernel`.
- **The repo does not declare these anywhere** — install at your own discretion.

### 10.2 Install

No install step exists in the repo. To make it runnable on a fresh environment:

```bash
# NOT provided by the repo — inferred
pip install pandas numpy scipy statsmodels matplotlib seaborn ipykernel
```

### 10.3 Generate the dataset (optional — the CSV is already committed)

```bash
py generate_superstore.py
# Output: Sample - Superstore.csv  (in the current working directory)
```

### 10.4 Run the analysis

```bash
# As a notebook (kernel must be registered)
jupyter notebook superstore_eda.ipynb
# or execute non-interactively:
python -m nbconvert --to notebook --execute superstore_eda.ipynb
```

### 10.5 Build

**Not applicable** — there is no build step, bundler, or packaging target.

### 10.6 Test

```bash
# The only test-like script in the repo (no assertions):
python testing.py
```

### 10.7 Deploy

**Not applicable** — no serving or deployment target exists.

---

## 11. Testing and quality

| Area | Tool / practice | Present in repo? | Notes |
|---|---|---|---|
| Unit / integration tests | pytest / unittest | **No** | No `tests/` directory, no test files. |
| Notebook execution | `nbconvert --execute` | Not referenced | Verified externally for this document (0 errors, 33 cells). |
| Smoke check | `testing.py` | **Yes** | 6 lines: three `groupby(...)[...].mean().round()` prints labelled Q1/Q2. No assertions, no pass/fail, no framework. |
| Linting | flake8 / ruff / pylint | **No** | No config files, no lint step. |
| Formatting | black / isort | **No** | Not enforced. |
| Type checking | mypy / pyright | **No** | No type annotations anywhere. |
| Coverage | coverage / pytest-cov | **No** | No reporting. |
| CI | GitHub Actions | **No** | `.github/workflows` absent. |
| Reproducibility | RNG seed | **Yes** | `SEED = 42` in both the generator and the notebook. |

**Verdict:** quality assurance is manual. The only automated check, `testing.py`, cannot fail.

---

## 12. Security notes

### 12.1 Auth / authorization

Not applicable. There is no authentication, no user accounts, no sessions, no permissions model,
and no network-facing surface.

### 12.2 Input validation

- The only external input is the CSV read in `load_superstore()`. Validation is limited to file
  existence and extension; there is no schema validation (column names, types, ranges) and the
  loader trusts whatever `pd.read_csv` returns.
- `pd.to_datetime(..., errors='coerce')` silently turns unparseable dates into `NaT` — which is
  exactly how the bug in §13.1 hid for 9,994 rows.
- `df['Profit'] / df['Sales']` (Profit Margin) would raise on zero `Sales`; `Sales` is always
  positive in the generated data, so this does not trigger, but it is unguarded.

### 12.3 Secrets handling

**No secrets are present.** No API keys, tokens, passwords, or connection strings appear in the
repo, and none are required. No `.gitignore` exists, so if a secret were ever added it would be
committed by default.

### 12.4 Visible risks

| Risk | Severity | Detail |
|---|---|---|
| Silent data corruption via `errors='coerce'` | **High** | 60.93 % of `Ship Date` parsed to `NaT` without any warning, producing negative `Ship Days`. No null-check asserts this away (§13.1). |
| No dependency manifest | **Medium** | Two of three interpreters on this machine cannot run the code; a new developer has no list of what to install. |
| Unasserted "tests" | **Medium** | `testing.py` prints numbers and cannot fail; it gives false confidence. |
| Committed generated artefact | **Low** | `Sample - Superstore.csv` is synthesised from a public script committed alongside it; the source of truth is ambiguous. |
| No `.gitignore` | **Low** | `__pycache__`, `.ipynb_checkpoints`, `*.pyc`, and outputs would be added by accident. |
| Notebook overwrites figures on rerun | **Low** | `savefig` clobbers `fig_*.png`; no versioning of outputs. |

---

## 13. Known issues and improvement suggestions

### 13.1 ⚠️ Date parsing is silently wrong (verified)

`_detect_dayfirst()` in `superstore_eda.ipynb` (cell `parse-dates`) inspects **only the first
non-null value of each column** and decides `dayfirst` per column:

```python
def _detect_dayfirst(series):
    sample = str(series.dropna().iloc[0]) ...
    parts  = sample.split('/')
    return len(parts) == 3 and int(parts[0]) > 12
```

The file is `DD/MM/YYYY` throughout. For `Order Date` the first value is `25/06/2016` → `25 > 12`
→ `dayfirst=True` ✓ (0 NaT). For `Ship Date` the first value is `02/07/2016` → `2 > 12` is
**False** → `dayfirst=False` ✗. Every `Ship Date` whose day exceeds 12 then fails and becomes
`NaT`.

**Measured impact (recomputed):** `Ship Date` NaT = **6,089 of 9,994 (60.93 %)** — which is exactly
what the notebook's own `missing_values_report` prints in §3. Consequently `Ship Days` is also
60.93 % NaN and the recorded `fig_ship_mode.png` table shows nonsense such as
`First Class mean = -31.50` days.

**Corrected values** (forcing `dayfirst=True`): `Ship Days` non-null, range 0–7;
`First Class` mean 1.5, `Same Day` 0.0, `Second Class` 3.0, `Standard Class` 5.5 (median 6.0).

**Fix:** stop inferring — the schema is known. Use a single explicit format per column:

```python
df[col] = pd.to_datetime(df[col].astype(str), format='%d/%m/%Y', errors='coerce')
```
and assert `df['Ship Date'].isna().sum() == 0` so a regression cannot hide again.

### 13.2 ⚠️ Narrative contradicts the notebook's own recorded outputs

The markdown prose asserts conclusions that the cells immediately above it *disprove*. Verified
against the notebook's own printed outputs (all five tests are unaffected by §13.1, so these are
independent defects):

| Location | What the notebook prints | What the narrative says | Verdict |
|---|---|---|---|
| §9.2 `h2-anova` (26) | `Result : FAIL TO REJECT H0` — `F=0.3535`, `p=7.8664e-01`, `eta2=0.0001` | "ANOVA **rejects** equal-means across regions" (§9.2 header + §7 + executive summary) | **Contradiction** |
| §9.2 `h2-tukey` (27) | All 6 pairs `reject: False` | "Tukey HSD pinpoints exactly which pairs differ: the Central region is significantly below the West" | **Contradiction** |
| §9.4 `h4-chisq` (29) | `Result : FAIL TO REJECT H0` — `chi2=1.6851`, `p=9.4627e-01`, `Cramér's V=0.0092` | "Chi-square is **significant**" and summary table marks H4 "**Confirmed**" | **Contradiction** |
| §7 `seg-region-heatmap` | Every segment×region `Avg_Margin` is negative | "Central region shows negative or near-zero profit margins across all segments — this is structural" (implying Central is worst) | **Reversed**: Central has the *least negative* margins of all four regions |
| §7 `seg-region-heatmap` | Home Office West margin = −1.82 % | "Home Office in the West generates the highest average margin percentage" | True only as the *least negative*; the narrative omits that **all 12 margins are negative** |
| §6.4 `shipmode-box` (18) | Corrected `Standard Class` median = 6.0 | "Standard Class median is **5** days" | Off by one |
| §1 intro | Consumer = 4,994 / 9,994 = 50.0 % | "Consumer segment dominates volume (~**52**%)" | Slight overstatement |
| §5.2 `quarterly-trend` (14) | Seasonality index ≥ 1.2 flags **no month** (output block is empty) | "March also shows an above-average spike"; "Slow months (Feb, **Apr**–May)" — April's index is 1.05, *above* average | Overstated |

The root cause is likely that the prose was written against the *expected* real-dataset result
while the recorded outputs came from the (buggy) run. Either way, the deliverable is internally
inconsistent.

**Fix:** regenerate the narrative from the actual outputs, or automate it so prose is derived from
computed values rather than hand-written.

### 13.3 ⚠️ `Sample - Superstore2.csv` is a byte-identical duplicate

Both files are 2,079,966 bytes with the same SHA-256 prefix (`655c80981cf2e7c6`). `git log` shows it
was added in commit `f86fd04 "ho"` with no accompanying change. It is read by nothing and serves no
purpose. **Remove it** to avoid ambiguity about which file is the working dataset.

### 13.4 No dependency manifest (repeated from §11)

Add a `requirements.txt` (or `pyproject.toml`) pinning the versions in §4.1, plus a short
prerequisites section. At minimum document which interpreter worked.

### 13.5 ⚠️ The headline finding is circular — an artefact of the generator

The top-line recommendation — *"Cap discounts at 20%; profitability collapses beyond this
threshold"* — rests on H5: `point-biserial r=0.6392`, loss rate by band `0% → 12.84 %`,
`1-20% → 94.44 %`, `21-40% → 100 %`, `41-60% → 100 %`, `>60% → 100 %`.

That loss rate is **baked into the generator**, not discovered. The profit model
(`generate_superstore.py:215`) is:

```python
effective_margin = bm - discount * 1.8 + np.random.normal(0, 0.04)
```

`base_margin` (`bm`) ranges from −0.10 (Tables) to +0.37 (Copiers). Multiplying the discount by
1.8 means even a 10 % discount (×1.8 = 0.18) wipes out the margin of most sub-categories — hence
94.44 % of the `1-20%` band is loss-making *by construction*. The generator's `discount_freq`
(0.08–0.45) and the `*1.8` penalty were chosen, then the analysis "found" that discounts destroy
profit.

**Implication:** "discounts destroy profit" is a restatement of the generator's design assumption.
It is not evidence about a real business, and the recommendation to cap discounts at 20 % does not
follow from independent data.

**Fix:** (a) state this limitation explicitly in the notebook's "Limitations" section; (b) if the
generator is meant to be realistic, calibrate the discount multiplier against real margin data, or
make it configurable and run a sensitivity sweep so the conclusion is shown to depend on the
parameter; (c) re-run the analysis on the real Kaggle dataset (Option A) and compare.

### 13.6 `testing.py` is not a test

```python
import pandas as pd
df = pd.read_csv("Sample - Superstore.csv", encoding="windows-1252")
print(df.groupby("Discount")["Profit"].mean().round(1))      # Q1
print(df.groupby("Category")["Profit"].sum().round(0))       # Q2
print(df.groupby("Region")["Profit"].sum().round(0))         # Q2
```

It prints three numbers with no assertions, no expected values, and no exit-code signal. Rename it
(e.g. `quick_checks.py`) or convert it to real assertions. Also fix the `windows-1252`/`latin-1`
mismatch against the generator.

### 13.7 Statistical concerns

- **H2 (ANOVA) is non-significant** (`p = 0.79`, `η² = 0.00011` — a trivial effect), yet the
  regional recommendations (§7, §10) are built on it. The regional differences visible in the data
  (East $83.21 vs West $23.49 mean profit) are not statistically distinguishable at `α = 0.05`
  given the variance. The recommendation "Discount-governance audit for Central region" is not
  supported by the test that was run.
- **H3 (Welch) is also non-significant** (`p = 0.75`, Cohen's `d = −0.0075` — negligible), yet the
  narrative claims Corporate and Home Office "punch above their weight". The *mean* ordering is
  real (Home Office $125.48 > Corporate $41.37 > Consumer $24.81) but not significant in this
  sample — report it as an observed tendency, not a validated finding.
- **H4 chi-square is non-significant** (`p = 0.95`, `V = 0.0092`), but the text calls it
  significant.
- **H1 is the one genuinely validated test** (`r = −0.3466`, `p = 4.42e-280`, `R² = 0.1201`,
  slope `−4241.29`, 95 % CI `[−4466.36, −4016.21]`) — but see §13.5 for why its causal reading is
  unwarranted.
- **Mean-of-ratios vs ratio-of-totals:** `Profit Margin` is averaged per row in the segment×region
  heatmap, which weights every order equally regardless of sales size. That is why *all* 12 cells
  come out negative even though the overall margin is +2.1 %. The two quantities answer different
  questions; the notebook does not distinguish them and the narrative reads the mean-of-ratios as
  though it were true margin.

### 13.8 Minor issues

- **`Duplicate (Order ID + Product ID)` check is meaningless** — `Product ID` is unique per
  sub-category instance, so the pair cannot repeat by construction. A useful check would be
  `Order ID` alone (which *should* repeat across line items) or a full-row hash.
- **`Postal Code` is read as int**, silently dropping leading zeros (e.g. `02138` → `2138`).
- **`random_date()` hardcodes 2014–2017** with no parameters exposed for reuse; the year weights
  `[0.18, 0.22, 0.27, 0.33]` and month weights are magic.
- **`customer_names` pool of 50 names** mapped modulo 50 from 800 customers means many customers
  share a name, and the pool is not representative.
- **No `.gitignore`** — `__pycache__`, `.ipynb_checkpoints`, and generated PNGs would pollute the
  history (the checkpoint is already tracked; the PNGs are committed outputs, which is fine for
  sharing but worth noting).
- **`testing.py` and the notebook disagree on the CSV encoding** (`windows-1252` vs `latin-1`).
- **`_is_string_dtype` uses `pandas.api.types`** inside a hot path — acceptable, but note it would
  need revisiting if pandas drops `is_string_dtype`.

### 13.9 Suggested improvement roadmap

| Priority | Action | Rationale |
|---|---|---|
| 1 | Fix `Ship Date` parsing with an explicit `%d/%m/%Y` format + a null-count assertion | Removes the single largest data defect (§13.1). |
| 2 | Align narrative with actual test outcomes (H2, H3, H4) | The deliverable is currently self-contradictory (§13.2). |
| 3 | Disclose that `Sample - Superstore.csv` is synthetic and that the discount result is a generator assumption (§13.5) | Stops a reader from treating a modelling choice as a business fact. |
| 4 | Add a `requirements.txt` pinning §4.1's versions + a documented working interpreter | Makes the project runnable on a fresh machine. |
| 5 | Delete `Sample - Superstore2.csv` | Removes a confusing duplicate. |
| 6 | Convert `testing.py` into real assertions, or add `pytest` | The only "test" cannot fail. |
| 7 | Distinguish mean-of-ratios from ratio-of-totals in the margin analysis | Prevents the all-negative-margins misreading (§13.7). |
| 8 | Add a `.gitignore` and a short `README.md` with install/run/test steps | Closes the documentation gaps in §9 and §10. |
| 9 | Re-run on the real Kaggle dataset (Option A) and diff the findings | Validates whether the conclusions survive real data. |
| 10 | Add schema validation to `load_superstore()` (expected columns, dtypes, ranges) | Catches corruption early instead of silently coercing. |

---

## Appendix A — Verification method

To avoid documenting assumptions, the following were executed rather than inferred:

1. **Notebook execution** — `python -m nbconvert --to notebook --execute --output exec_out.ipynb
   superstore_eda.ipynb` under Python 3.14.0 / pandas 3.0.6: **0 errors across all 33 code cells**.
   Output comparison against the committed notebook found only the trivial `Styler` object-address
   difference — i.e. the notebook reproduces byte-for-byte, **including the 6,089 `Ship Date`
   nulls**.
2. **Independent recomputation** — a throwaway script re-derived every statistic with
   `dayfirst=True`, producing the ground-truth tables in §7.4 and §13.2.
3. **Dependency versions** — obtained by importing each module, not guessed.
4. **Duplicate detection** — byte-length plus SHA-256 prefix comparison of the two CSVs.
5. **Git history** — `git log --stat` confirmed the three commits and the provenance of every file.

All throwaway verification scripts were deleted after use; the working tree contains only the
original 20 files plus this document.

## Appendix B — What could not be determined

| Item | Status |
|---|---|
| The author's identity beyond the notebook header (`[Suvam SuryaKanta Nayak]`) and the GitHub remote (`nayaksuvamsuryakanta-a11y`) | Not derivable from code |
| Whether the committed CSV is intended to *replace* the real Kaggle dataset or merely bootstrap offline runs | Not stated in code; both readings are plausible |
| The intended reviewer / grading criteria for "Task 2" | Not in the repo |
| Why `Sample - Superstore2.csv` was added (commit message: `ho`) | Not explained; appears accidental |
| The environment in which the notebook was originally authored (kernel spec is only `python3`) | Not recorded beyond that |
| Whether the negative `Ship Days` in the recorded outputs were noticed at the time | Not determinable |
| Any intended deployment or CI target | Not present in code |
| Exact versions of pandas/scipy/etc. used at authoring time | Not pinned; only current versions are known |