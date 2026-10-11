# DV2 data files — Education Equity and Disadvantage in Australia

All files are produced by `prepare_data.py` from the raw downloads in `raw/`. Re-run it to rebuild.

| File | Rows | One row per | Use for |
|---|---|---|---|
| `schools.csv` | 9,755 | School (2025) | Dot / proportional-symbol map, strip plot, ridgeline, SEA stacked bar |
| `lga.csv` | 547 | Local Government Area (2021 boundaries) | Choropleth, bivariate choropleth, scatter |
| `aedc_by_seifa.csv` | 2,268 | State × SEIFA quintile × AEDC domain × year | Heatmap, slope/dumbbell |
| `aedc_by_remoteness.csv` | 1,932 | State × remoteness × AEDC domain × year | Dumbbell, small multiples |
| `uni_equity.csv` | 98 | Equity group × year (2011–2024) | Waffle, line chart |
| `aedc_lga_years.csv` | 548 | LGA, with one column per AEDC year (2009 … 2024) = % vulnerable on 1+ domains | Small-multiple maps (repeat) |

## Columns

**schools.csv** — `id` (ACARA SML ID), `name`, `suburb`, `state`, `sector` (Government/Catholic/Independent), `type` (Primary/Secondary/Combined/Special), `special` (1 = special school), `remoteness` (Major Cities … Very Remote), `lat`, `lon`, `lga_code` (joins to lga.csv), `icsea` (blank for 132 schools, mostly special schools), `sea_bottom_pct` / `sea_lowmid_pct` / `sea_upmid_pct` / `sea_top_pct` (% of students in each socio-educational quarter), `enrolments`, `indigenous_pct`, `lbote_pct` (% language background other than English).

**lga.csv** — `lga_code` (join key to the ASGS 2021 LGA TopoJSON), `lga_name`, `state`, `irsd_score` / `irsd_decile` (SEIFA 2021, decile 1 = most disadvantaged), `population` (2021), `aedc_children_2024`, `aedc_vuln1_pct_2024` (% vulnerable on 1+ domains), `aedc_vuln2_pct_2024` (2+ domains), `y12_pct_20_24`, `y12_pct_25_34`, `y12_pct_15plus` (% who completed Year 12 or equivalent, Census 2021), `pop_20_24`, `schools` (count), `median_icsea`.

**aedc_by_seifa.csv / aedc_by_remoteness.csv** — `state` ("Australia" = sum of the eight states), group column (`seifa_quintile` or `remoteness`; "All children" = state total), `domain` (5 domains + "One or more domains" + "Two or more domains"), `year` (2009–2024), `n_valid`, `n_vulnerable`, `pct_vulnerable`.

**uni_equity.csv** — `group`, `year`, `students` (domestic higher-education students), `share_pct` (% of all domestic students).

## Caveats to mention on the page
- **AEDC suppression:** ~97 small LGAs have no 2024 % (AEDC does not publish where too few children were assessed). Show these as "Not published" (grey), not zero.
- **Census small areas:** Year 12 % is blank where fewer than 50 people in that age group answered, because ABS randomly adjusts small counts for privacy. `y12_pct_25_34` has the best coverage (523 LGAs) and is the recommended measure for the map; `y12_pct_15plus` is skewed by older age structure.
- **AEDC merged categories:** SA, TAS and ACT publish "Quintile 3/Missing" combined and ACT publishes "Major Cities/Inner Regional" combined; these were counted as Quintile 3 and Major Cities respectively (Missing is <1% of children).
- **University series:** Low SES / Regional / Remote use the newest available classification for each year (SEIFA 2011→2016→2021; ASGS 2011→2016→2021), so small steps at 2016 and 2021 are classification changes, not real changes. Low SES = bottom 25% of areas, so 25% is the "fair share" benchmark.
- **Mixed years:** schools 2025, AEDC 2024, university 2024, SEIFA and Census 2021 (latest available).

## Sources
- ACARA, School Profile 2025 and School Location 2025 — https://acara.edu.au/contact-us/acara-data-access
- ABS, Socio-Economic Indexes for Areas (SEIFA) 2021, LGA Indexes — https://www.abs.gov.au/statistics/people/people-and-communities/socio-economic-indexes-areas-seifa-australia/latest-release
- ABS, 2021 Census General Community Profile DataPack (LGA), table G16 — https://www.abs.gov.au/census/find-census-data/datapacks
- Australian Early Development Census, Data by LGA / SEIFA / Remoteness 2009–24 — https://www.aedc.gov.au/data-hub/public-data/additional-data
- Department of Education, Higher Education Statistics 2024 Section 11 Equity Groups — https://www.education.gov.au/higher-education-statistics/resources/2024-section-11-equity-groups
- Map boundaries: ABS ASGS Edition 3 (2021) Local Government Areas — https://digital.atlas.gov.au/datasets/digitalatlas::abs-asgs-edition-3-2021-local-government-areas/about
