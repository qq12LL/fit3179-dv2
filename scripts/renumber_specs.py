"""
Renumbers the chart specification files in specs/ so their numbers follow the order
the charts appear on the web page, and updates every reference to them
(js/main.js, README.md, index.html). Uses `git mv` so Git records them as renames.

Run once from the repo root:  python3 scripts/renumber_specs.py
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# old file name -> new file name (new number = position on the page)
RENAME = {
    "01_map_bivariate.vl.json":         "01_map_bivariate.vl.json",
    "11_overview_detail_rank.vl.json":  "02_overview_detail_rank.vl.json",
    "02_heatmap_domains.vl.json":       "03_heatmap_domains.vl.json",
    "03_dumbbell_remoteness.vl.json":   "04_dumbbell_remoteness.vl.json",
    "12_small_multiples_years.vl.json": "05_small_multiples_years.vl.json",
    "04_map_schools_strip.vl.json":     "06_map_schools_strip.vl.json",
    "05_ridgeline_sector.vl.json":      "07_ridgeline_sector.vl.json",
    "06_stacked_sea_sector.vl.json":    "08_stacked_sea_sector.vl.json",
    "07_map_year12.vl.json":            "09_map_year12.vl.json",
    "08_scatter_irsd_y12.vl.json":      "10_scatter_irsd_y12.vl.json",
    "09_waffle_uni.vl.json":            "11_waffle_uni.vl.json",
    "10_line_uni_trend.vl.json":        "12_line_uni_trend.vl.json",
}

specs = ROOT / "specs"
if not (specs / "11_overview_detail_rank.vl.json").exists():
    raise SystemExit("Looks like the files are already renumbered - nothing to do.")

# 1. rename files (via temporary names so no new name ever clashes with an old one)
for old in RENAME:
    subprocess.run(["git", "mv", f"specs/{old}", f"specs/tmp_{old}"], cwd=ROOT, check=True)
for old, new in RENAME.items():
    subprocess.run(["git", "mv", f"specs/tmp_{old}", f"specs/{new}"], cwd=ROOT, check=True)

# 2. update references in one pass (a single regex, so a replaced name is never replaced twice)
pattern = re.compile("|".join(re.escape(o) for o in RENAME))
for name in ["js/main.js", "README.md", "index.html"]:
    f = ROOT / name
    if f.exists():
        text = pattern.sub(lambda m: RENAME[m.group(0)], f.read_text())
        f.write_text(text)

# 3. README chart table: put the rows back in page order
readme = ROOT / "README.md"
if readme.exists():
    lines = readme.read_text().split("\n")
    rows = [i for i, l in enumerate(lines) if re.match(r"\| \d+ \| `\d\d_", l)]
    if rows:
        block = [lines[i] for i in rows]
        def key(row):
            num = int(re.search(r"`(\d\d)_", row).group(1))
            part = 1 if "(bottom)" in row else 0
            return (num, part)
        block.sort(key=key)
        block = [re.sub(r"^\| \d+ \|", f"| {n} |", r) for n, r in enumerate(block, 1)]
        for i, r in zip(rows, block):
            lines[i] = r
        readme.write_text("\n".join(lines))

print("Done. Spec files now follow the page order:")
for new in RENAME.values():
    print("  specs/" + new)
