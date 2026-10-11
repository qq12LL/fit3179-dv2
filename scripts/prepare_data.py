"""
FIT3179 DV2 - Education Equity and Disadvantage in Australia
Data preparation: turns the raw downloads in raw/ into small, tidy CSVs in data/
that Vega-Lite can load directly.

Run from the repo root:  python scripts/prepare_data.py
Needs: pandas, openpyxl
"""
import io
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw"      # raw downloads (not committed - see README for links)
OUT = ROOT / "data"     # small files loaded by the web page
OUT.mkdir(exist_ok=True)

YEARS = [2009, 2012, 2015, 2018, 2021, 2024]
AEDC_DOMAINS = {
    "Health": "Physical health",
    "Social": "Social competence",
    "Emotional": "Emotional maturity",
    "Language": "Language & thinking",
    "Communication": "Communication",
    "One or more": "One or more domains",
    "Two or more": "Two or more domains",
}


def to_num(s):
    return pd.to_numeric(s, errors="coerce")


# ---------------------------------------------------------------- 1. schools
def build_schools():
    prof = pd.read_excel(RAW / "School_Profile_2025.xlsx", sheet_name="SchoolProfile 2025")
    loc = pd.read_excel(RAW / "School_Location_2025.xlsx", sheet_name="SchoolLocations 2025")
    loc = loc[["ACARA SML ID", "Latitude", "Longitude", "Special school",
               "Local Government Area", "Local Government Area Name"]]
    df = prof.merge(loc, on="ACARA SML ID", how="left", validate="one_to_one")

    out = pd.DataFrame({
        "id": df["ACARA SML ID"],
        "name": df["School Name"],
        "suburb": df["Suburb"],
        "state": df["State"],
        "sector": df["School Sector"],
        "type": df["School Type"],
        "remoteness": df["Geolocation"],
        "lat": df["Latitude"].round(4),
        "lon": df["Longitude"].round(4),
        "lga_code": to_num(df["Local Government Area"]).astype("Int64"),
        "icsea": to_num(df["ICSEA"]).astype("Int64"),
        "sea_bottom_pct": to_num(df["Bottom SEA Quarter (%)"]).astype("Int64"),
        "sea_lowmid_pct": to_num(df["Lower Middle SEA Quarter (%)"]).astype("Int64"),
        "sea_upmid_pct": to_num(df["Upper Middle SEA Quarter (%)"]).astype("Int64"),
        "sea_top_pct": to_num(df["Top SEA Quarter (%)"]).astype("Int64"),
        "enrolments": to_num(df["Total Enrolments"]).astype("Int64"),
        "indigenous_pct": to_num(df["Indigenous Enrolments (%)"]).astype("Int64"),
    })
    out = out.dropna(subset=["lat", "lon"])
    out.to_csv(OUT / "schools.csv", index=False)
    return out


# ---------------------------------------------------------------- 2. LGA table
STATE_NAMES = ["New South Wales", "Victoria", "Queensland", "South Australia",
               "Western Australia", "Tasmania", "Northern Territory",
               "Australian Capital Territory"]


def read_aedc_block(path, sheet):
    """AEDC 2009-24 tables: col1=code, col2=name, cols 3-8 = children with valid scores by year.
    'One or more'/'Two or more' sheets: cols 9-20 = (n vulnerable, %) pairs by year.
    Single-domain sheets: cols 9-20 on track, 21-32 at risk, 33-44 vulnerable.
    Suppressed values ('#', '*') become blank. Returns tidy rows incl. state total rows."""
    raw = pd.read_excel(path, sheet_name=sheet, header=None)
    header_text = " ".join(map(str, raw.iloc[:8].values.ravel()))
    vstart = 33 if "on track" in header_text else 9
    rows = []
    state = None
    for _, r in raw.iloc[6:].iterrows():
        code, name = r[1], r[2]
        if pd.isna(code):
            continue
        code_s = str(code).strip()
        if pd.isna(name):
            if code_s in STATE_NAMES:      # state total row
                state, name, code = code_s, code_s, None
            else:                          # footnotes etc.
                continue
        elif state is None:
            continue
        for i, y in enumerate(YEARS):
            rows.append({
                "state": state, "code": code, "name": str(name).strip(), "year": y,
                "n_valid": to_num(pd.Series([r[3 + i]]))[0],
                "n_vulnerable": to_num(pd.Series([r[vstart + 2 * i]]))[0],
                "pct_vulnerable": to_num(pd.Series([r[vstart + 1 + 2 * i]]))[0],
            })
    return pd.DataFrame(rows)


def build_lga():
    # SEIFA 2021 by LGA (Table 1: all four indexes)
    s = pd.read_excel(RAW / "Local_Government_Area_Indexes_SEIFA_2021.xlsx",
                      sheet_name="Table 1", header=None, skiprows=6)
    s = s[to_num(s[0]).notna()]
    seifa = pd.DataFrame({
        "lga_code": s[0].astype(int),
        "lga_name": s[1],
        "irsd_score": to_num(s[2]),
        "irsd_decile": to_num(s[3]).astype("Int64"),
        "population": to_num(s[10]).astype("Int64"),
    })

    # AEDC 2024 by LGA - vulnerable on one or more / two or more domains
    a1 = read_aedc_block(RAW / "aedc-lga-2009-24.xlsx", "LGA One or more")
    a2 = read_aedc_block(RAW / "aedc-lga-2009-24.xlsx", "LGA Two or more")
    keep = lambda d: d[(d.year == 2024) & d.code.notna()].assign(lga_code=lambda x: x.code.astype(int))
    a1, a2 = keep(a1), keep(a2)
    aedc = a1[["lga_code", "state", "n_valid", "pct_vulnerable"]].rename(columns={
        "n_valid": "aedc_children_2024", "pct_vulnerable": "aedc_vuln1_pct_2024"})
    aedc = aedc.merge(a2[["lga_code", "pct_vulnerable"]].rename(
        columns={"pct_vulnerable": "aedc_vuln2_pct_2024"}), on="lga_code", how="left")

    # Census 2021 G16 - highest year of school completed
    z = zipfile.ZipFile(RAW / "2021_GCP_LGA_for_AUS_short-header.zip")
    base = "2021 Census GCP Local Government Areas for AUS/"
    g16a = pd.read_csv(io.BytesIO(z.read(base + "2021Census_G16A_AUST_LGA.csv")))
    g16b = pd.read_csv(io.BytesIO(z.read(base + "2021Census_G16B_AUST_LGA.csv")))
    g = g16a.merge(g16b, on="LGA_CODE_2021")
    g = g.copy()
    g["lga_code"] = g["LGA_CODE_2021"].str.replace("LGA", "").astype(int)

    def y12(age_y12, age_tot, age_ns):
        stated = g[age_tot] - g[age_ns]           # exclude "not stated"
        # ABS randomly perturbs small Census cells, so tiny areas can exceed 100%.
        # Only report the rate where at least 50 people in the age group stated an answer.
        return (g[age_y12] / stated * 100).where(stated >= 50).clip(upper=100).round(1)

    census = pd.DataFrame({
        "lga_code": g["lga_code"],
        "y12_pct_20_24": y12("P_Y12e_20_24", "P_Tot_20_24_yrs", "P_Hghst_yr_schl_ns_20_24_yrs"),
        "y12_pct_25_34": y12("P_Y12e_25_34", "P_Tot_25_34_yrs", "P_Hghst_yr_schl_ns_25_34_yrs"),
        "y12_pct_15plus": y12("P_Y12e_Tot", "P_Tot_Tot", "P_Hghst_yr_schl_ns_Tot"),
        "pop_20_24": g["P_Tot_20_24_yrs"],
    })

    # school summary per LGA (from schools.csv logic)
    sch = pd.read_csv(OUT / "schools.csv")
    sch_lga = sch.groupby("lga_code").agg(
        schools=("id", "count"),
        median_icsea=("icsea", "median"),
    ).reset_index()

    lga = (seifa.merge(aedc, on="lga_code", how="left")
                .merge(census, on="lga_code", how="left")
                .merge(sch_lga, on="lga_code", how="left"))
    # tidy
    lga["aedc_vuln1_pct_2024"] = lga["aedc_vuln1_pct_2024"].round(1)
    lga["aedc_vuln2_pct_2024"] = lga["aedc_vuln2_pct_2024"].round(1)
    lga["median_icsea"] = lga["median_icsea"].round(0).astype("Int64")
    lga["schools"] = lga["schools"].astype("Int64")
    lga["aedc_children_2024"] = to_num(lga["aedc_children_2024"]).astype("Int64")
    # state name from code prefix (ASGS: 1 NSW ... 9 Other)
    states = {1: "NSW", 2: "VIC", 3: "QLD", 4: "SA", 5: "WA", 6: "TAS", 7: "NT", 8: "ACT", 9: "OT"}
    lga["state"] = (lga["lga_code"] // 10000).map(states)
    lga.to_csv(OUT / "lga.csv", index=False)
    return lga


# ---------------------------------------------------------------- 3/4. AEDC by SEIFA / remoteness
def build_aedc_group(fname, prefix, outname, group_label):
    frames = []
    for key, label in AEDC_DOMAINS.items():
        d = read_aedc_block(RAW / fname, f"{prefix} {key}")
        d.loc[d.code.isna(), "name"] = "All children"   # state total rows
        d["domain"] = label
        frames.append(d)
    d = pd.concat(frames)
    # SA/TAS/ACT publish 'Quintile 3/Missing' and ACT 'Major Cities/Inner Regional' as merged rows.
    # 'Missing' is <1% of children and ACT is almost entirely Major City, so fold them in.
    d["name"] = d["name"].replace({
        "Quintile 3/Missing": "Quintile 3",
        "Major Cities of Australia/Inner Regional Australia": "Major Cities of Australia",
    })
    d = d[d["name"] != "Missing"]
    # National totals = sum of the eight states (the file has no Australia block)
    d = d[d["name"].notna()]
    nat = (d.groupby(["name", "domain", "year"], as_index=False)[["n_valid", "n_vulnerable"]].sum())
    nat["pct_vulnerable"] = nat["n_vulnerable"] / nat["n_valid"] * 100
    nat["state"] = "Australia"
    d = pd.concat([nat, d[["state", "name", "domain", "year", "n_valid", "n_vulnerable", "pct_vulnerable"]]])
    d = d.rename(columns={"name": group_label})
    d["n_valid"] = d["n_valid"].astype("Int64")
    d["n_vulnerable"] = d["n_vulnerable"].astype("Int64")
    d["pct_vulnerable"] = d["pct_vulnerable"].round(1)
    d = d[["state", group_label, "domain", "year", "n_valid", "n_vulnerable", "pct_vulnerable"]]
    d.to_csv(OUT / outname, index=False)
    return d


# ---------------------------------------------------------------- 5. University equity time series
def build_uni_equity():
    x = pd.read_excel(RAW / "2024_Section11_Equity_Groups.xlsx", sheet_name="11.1", header=None)
    years = [int(v) for v in x.iloc[2, 1:15]]
    body = x.iloc[3:28, :15].copy()
    body.columns = ["group"] + years
    body["group"] = body["group"].astype(str)

    def series(pattern_list):
        """Take, for each year, the value from the newest classification that has data
        (e.g. Low SES uses 2011 SEIFA to 2015, 2016 SEIFA 2016-2020, 2021 SEIFA 2021+)."""
        res = {}
        for y in years:
            val = None
            for pat in pattern_list:  # newest first
                row = body[body.group.str.startswith(pat)]
                if len(row):
                    v = to_num(row[y]).iloc[0]
                    if pd.notna(v) and v > 0:
                        val = v
                        break
            res[y] = val
        return res

    groups = {
        "Low SES": ["Low SES by SA1 (2021", "Low SES by SA1 (2016", "Low SES by SA1 (2011"],
        "Regional": ["Regional (2021", "Regional (2016", "Regional (2011", "Regional (2006"],
        "Remote": ["Remote (2021", "Remote (2016", "Remote (2011", "Remote (2006"],
        "First Nations": ["First Nations"],
        "Disability": ["Students with a disability"],
        "Non-English speaking background": ["Students from a Non-English"],
        "Total domestic students": ["Total"],
    }
    rows = []
    for g, pats in groups.items():
        for y, v in series(pats).items():
            rows.append({"group": g, "year": y, "students": v})
    d = pd.DataFrame(rows)
    tot = d[d.group == "Total domestic students"].set_index("year")["students"]
    d["share_pct"] = (d["students"] / d["year"].map(tot) * 100).round(2)
    d["students"] = d["students"].astype("Int64")
    d.to_csv(OUT / "uni_equity.csv", index=False)
    return d


def build_aedc_lga_years():
    """Wide table for the small-multiple maps: % of children vulnerable on 1+ domains,
    one column per AEDC year (2009 ... 2024), keyed by 2021 LGA code."""
    a = read_aedc_block(RAW / "aedc-lga-2009-24.xlsx", "LGA One or more")
    a = a[a.code.notna()].copy()
    a["lga_code"] = a["code"].astype(int)
    w = (a.pivot_table(index="lga_code", columns="year", values="pct_vulnerable")
          .round(1).reset_index())
    w.columns = ["lga_code"] + [str(c) for c in w.columns[1:]]
    w.to_csv(OUT / "aedc_lga_years.csv", index=False)
    return w


def build_uni_share_2024(uni):
    """Share of 2024 domestic university students vs that group's share of the population.
    Low SES = bottom 25% of areas by definition, so the fair-share benchmark is 25%.
    First Nations benchmark = share of the 2021 Census population (table G01)."""
    z = zipfile.ZipFile(RAW / "2021_GCP_LGA_for_AUS_short-header.zip")
    g01 = pd.read_csv(io.BytesIO(z.read(
        "2021 Census GCP Local Government Areas for AUS/2021Census_G01_AUST_LGA.csv")))
    fn_pop = g01["Indigenous_P_Tot_P"].sum() / g01["Tot_P_P"].sum() * 100
    u = uni[uni.year == 2024].set_index("group")["share_pct"]
    d = pd.DataFrame([
        {"group": "Low SES", "label": "Students from low-SES areas",
         "uni_share_pct": round(u["Low SES"], 1), "population_share_pct": 25.0},
        {"group": "First Nations", "label": "First Nations students",
         "uni_share_pct": round(u["First Nations"], 1), "population_share_pct": round(fn_pop, 1)},
    ])
    d.to_csv(OUT / "uni_share_2024.csv", index=False)
    return d


if __name__ == "__main__":
    s = build_schools()
    l = build_lga()
    a = build_aedc_group("aedc-seifa-2009-24.xlsx", "SEIFA", "aedc_by_seifa.csv", "seifa_quintile")
    r = build_aedc_group("aedc-remoteness-2009-24.xlsx", "Remoteness", "aedc_by_remoteness.csv", "remoteness")
    u = build_uni_equity()
    build_uni_share_2024(u)
    build_aedc_lga_years()
    for f in sorted(OUT.glob("*.csv")):
        print(f"{f.name:28s} {f.stat().st_size/1024:8.1f} KB")
