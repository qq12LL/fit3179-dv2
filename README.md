# The Postcode Lottery: education equity in Australia

**FIT3179 Data Visualisation 2 · Monash University**

A single-page, scrolling data story showing how where an Australian child grows up shapes their education at four stages: early childhood, school, finishing Year 12 and university. It is built with **Vega-Lite** and hosted on **GitHub Pages**.

🔗 **Live page:** `https://<your-github-username>.github.io/<repo-name>/`

---

## Repository layout

```
index.html                  the page (narrative text + chart placeholders)
css/style.css               layout and typography (serif titles, sans-serif body)
js/main.js                  embeds each chart with vega-embed
js/vl-config.json           shared chart styling (fonts, colours, axes)
specs/                      ONE human-readable Vega-Lite JSON file per chart
data/                       small cleaned data files the page loads (about 1.9 MB total)
  README.md                 column dictionary, caveats, sources
scripts/prepare_data.py     raw downloads -> data/*.csv
scripts/make_boundaries.py  ABS boundaries -> data/australia_lga_2021.topo.json
raw/                        (not committed) original downloads, see "Data sources"
```

## The charts (12 spec files, 13 charts, 4 map idioms)

| # | Spec | Idiom | What it shows |
|---|------|-------|---------------|
| 1 | `01_map_bivariate.vl.json` | **Bivariate choropleth map** | Area disadvantage × % of 5-year-olds developmentally vulnerable, by council area |
| 2 | `02_heatmap_domains.vl.json` | Heatmap | % vulnerable in 5 development areas × 5 disadvantage quintiles |
| 3 | `03_dumbbell_remoteness.vl.json` | Dumbbell / dot strip | % vulnerable from major cities to very remote, per development area |
| 4 | `04_map_schools_strip.vl.json` (top) | **Proportional symbol map** | Every school: size = enrolments, colour = ICSEA |
| 5 | `04_map_schools_strip.vl.json` (bottom) | Jittered strip plot + medians | School ICSEA by remoteness; **brushing filters the map**, dropdown filters sector |
| 6 | `05_ridgeline_sector.vl.json` | Ridgeline (density) plot | ICSEA distribution for Government, Catholic and Independent schools |
| 7 | `06_stacked_sea_sector.vl.json` | Normalised stacked bar | Students' family-background quarters by sector (enrolment-weighted) |
| 8 | `07_map_year12.vl.json` | **Choropleth map + city insets** | % of 25–34 year olds who finished Year 12, by council area; Sydney and Melbourne insets |
| 9 | `08_scatter_irsd_y12.vl.json` | Scatterplot + LOESS trend | Area disadvantage vs Year 12 completion |
| 10 | `09_waffle_uni.vl.json` | Waffle chart | Low-SES and First Nations students per 100 university students vs fair share |
| 11 | `10_line_uni_trend.vl.json` | Multi-line chart | Equity-group shares of university students, 2011–2024 |
| 12 | `11_overview_detail_rank.vl.json` | **Overview + detail (brush)** ranked bar chart | All 450 council areas ranked by % of children vulnerable; brushing the overview strip sets the detail chart's x-scale domain |
| 13 | `12_small_multiples_years.vl.json` | **Small-multiple choropleth maps** (`repeat` operator) | % of children vulnerable by council area, one map per AEDC year 2009–2024, shared colour scale |

All maps use an **Albers equal-area conic projection** (`conicEqualArea`, standard parallels 18°S and 36°S, the Australian convention), so council areas are compared at their true relative size.

## Munzner's What / Why / How (summary)

| | |
|---|---|
| **What** (data) | *Geometry* (council-area polygons, school points); *tables* of council areas (SEIFA score: quantitative; decile: ordinal; AEDC %: quantitative), schools (sector, remoteness: categorical/ordinal; ICSEA, enrolments, lat/lon: quantitative), and time series (year: ordinal; share: quantitative). |
| **Why** (tasks) | *Discover* and *present* the distribution of disadvantage; *compare* groups (sectors, remoteness, quintiles); *identify* outliers (remote communities, outer-suburban councils); *locate* schools of a given ICSEA (brushing); see *trends* over time. |
| **How** (encoding) | Area marks + colour (sequential, diverging, bivariate) for choropleths; point marks + **size** (enrolments) and **diverging colour** (ICSEA around the 1000 average) for schools; position on common scales for strip, dumbbell, scatter and line charts; length for normalised bars; small grid of area marks for the waffle. **Interaction:** tooltips, hover highlight, brush-and-link (strip → map), overview + detail (brushed overview sets the detail chart's scale domain), dropdown filter. **Facet:** small multiples via `repeat` (one map per year) and `facet` (waffle, ridgeline). **Reduce:** filtering; aggregation (medians, weighted sums, density estimates). |

## Run locally

The page loads its JSON and CSV files with `fetch`, so open it through a local web server rather than by double-clicking the file:

```bash
python -m http.server 8000
# then open http://localhost:8000
```

## Publish on GitHub Pages

1. Create a **public** repository on GitHub (e.g. `fit3179-dv2`).
2. Push this folder to it (see the commands below).
3. On GitHub: **Settings → Pages → Build and deployment → Source: Deploy from a branch → Branch: `main` / `(root)` → Save**.
4. After about a minute the page is live at `https://<username>.github.io/<repo-name>/`.

```bash
git remote add origin https://github.com/<username>/<repo-name>.git
git push -u origin main
```

## Rebuild the data (optional)

1. Download the raw files listed below into `raw/`.
2. `pip install pandas openpyxl rdata numpy` and `npm install -g mapshaper`
3. `python scripts/prepare_data.py` and `python scripts/make_boundaries.py`

## Data sources

- ACARA, School Profile 2025 & School Location 2025: https://acara.edu.au/contact-us/acara-data-access
- Australian Early Development Census, Data by LGA / SEIFA / Remoteness 2009–24: https://www.aedc.gov.au/data-hub/public-data/additional-data
- ABS, SEIFA 2021 (LGA Indexes): https://www.abs.gov.au/statistics/people/people-and-communities/socio-economic-indexes-areas-seifa-australia/latest-release
- ABS, 2021 Census GCP DataPack (LGA), tables G01 & G16: https://www.abs.gov.au/census/find-census-data/datapacks
- Department of Education, Higher Education Statistics 2024, Section 11 Equity Groups: https://www.education.gov.au/higher-education-statistics/resources/2024-section-11-equity-groups
- ABS ASGS Edition 3 (2021) LGA boundaries (CC BY 4.0), via absmapsdata (`data/lga2021.rda`): https://github.com/wfmackey/absmapsdata

## Libraries

[Vega 5.33](https://vega.github.io/vega/), [Vega-Lite 5.23](https://vega.github.io/vega-lite/), [Vega-Embed 6.29](https://github.com/vega/vega-embed), fonts *Source Serif 4* and *Source Sans 3* (Google Fonts, SIL Open Font Licence).
