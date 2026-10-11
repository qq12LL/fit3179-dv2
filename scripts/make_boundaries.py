"""
Builds data/australia_lga_2021.topo.json (council-area + state outlines) for the maps.

Source: ABS ASGS Edition 3 (2021) Local Government Areas, as packaged (already lightly
generalised, with area centroids) in the absmapsdata R package:
    https://github.com/wfmackey/absmapsdata  ->  data/lga2021.rda
Download that file into raw/ first.

Steps
  1. read the R data file and write a GeoJSON (drops the 19 "No usual address" /
     "Migratory" pseudo-areas, which have no shape)
  2. mapshaper: drop Other Territories (Christmas/Cocos/Jervis Bay islands), simplify
     to 10% of vertices (keeping every area), dissolve council areas into state outlines,
     export TopoJSON with two layers: "lga" and "states".  Result is about 375 KB.

Needs: pip install rdata numpy   and   npm install -g mapshaper
Run from the repo root:  python scripts/make_boundaries.py
"""
import json
import subprocess
import warnings
from pathlib import Path

import numpy as np
import rdata

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
RAW, OUT = ROOT / "raw", ROOT / "data"

df = rdata.conversion.convert(rdata.parser.parse_file(RAW / "lga2021.rda"),
                              default_encoding="utf8")["lga2021"]
features = []
for _, r in df.iterrows():
    polys = [[np.asarray(ring).round(5).tolist() for ring in poly] for poly in r.geometry]
    if not polys or not any(len(p) for p in polys):
        continue  # pseudo-areas without geometry
    features.append({
        "type": "Feature",
        "properties": {
            "lga_code": int(r.lga_code_2021),
            "lga_name": r.lga_name_2021,
            "state": r.state_name_2021,
            "cx": round(float(r.cent_long), 4),   # centroid, used to pick areas for city insets
            "cy": round(float(r.cent_lat), 4),
        },
        "geometry": {"type": "MultiPolygon", "coordinates": polys},
    })
geojson = RAW / "lga2021.geojson"
geojson.write_text(json.dumps({"type": "FeatureCollection", "features": features}))
print(len(features), "council areas written to", geojson)

subprocess.run([
    "mapshaper", str(geojson),
    "-filter", 'state != "Other Territories"',
    "-simplify", "10%", "weighted", "keep-shapes",
    "-clean",
    "-rename-layers", "lga",
    "-each", "state_name=state; delete state",
    "-dissolve", "state_name", "+", "name=states",
    "-each", "delete cx; delete cy", "target=states",
    "-o", "format=topojson", "quantization=1e5", "target=lga,states",
    str(OUT / "australia_lga_2021.topo.json"),
], check=True)
