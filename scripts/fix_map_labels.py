"""
Year 12 map: replace the "Sydney/Melbourne ... inset" text labels with
a box drawn around each city on the national map, a leader line, and a city name,
so readers can see exactly which area each inset zooms into.
Clips map shapes to the frame. Also removes the duplicated "Right: Sydney and Melbourne zoomed in." subtitle.

Also moves two-line map annotations above their leader lines (maps 01, 06, 09).
Safe to run more than once.

Run from the repo root:  python3 scripts/fix_map_labels.py
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec_path = ROOT / "specs" / "09_map_year12.vl.json"
spec = json.loads(spec_path.read_text())
main = spec["hconcat"][0]

# same boxes the insets use in their projection "fit"
BOXES = {
    "Sydney":    [[150.62, -33.55], [151.33, -34.12]],
    "Melbourne": [[144.55, -37.55], [145.50, -38.15]],
}
def box(name):
    (w, n), (e, s) = BOXES[name]
    ring = [[w, n], [e, n], [e, s], [w, s], [w, n]]   # clockwise
    return {"type": "Feature", "properties": {"city": name},
            "geometry": {"type": "Polygon", "coordinates": [ring]}}

# label position (in the ocean) and the box corner the leader line points to
LABELS = [
    {"city": "Sydney",    "lon": 156.0, "lat": -36.2, "lon2": 151.33, "lat2": -34.12, "align": "left"},
    {"city": "Melbourne", "lon": 139.0, "lat": -40.3, "lon2": 144.55, "lat2": -38.15, "align": "right"},
]
for d in LABELS:
    d["t"] = d["city"] + " (zoomed in at right)"

new_layers = [
    {   # outline of the area shown in each inset
        "data": {"values": [box("Sydney"), box("Melbourne")], "format": {"type": "json"}},
        "mark": {"type": "geoshape", "filled": False, "stroke": "#1d1712", "strokeWidth": 1.8}
    },
    {   # leader line from label to box
        "data": {"values": LABELS},
        "mark": {"type": "rule", "color": "#1d1712", "strokeWidth": 1, "strokeDash": [3, 2]},
        "encoding": {"longitude": {"field": "lon", "type": "quantitative"},
                     "latitude": {"field": "lat", "type": "quantitative"},
                     "longitude2": {"field": "lon2"}, "latitude2": {"field": "lat2"}}
    },
    {   # city name
        "data": {"values": LABELS},
        "mark": {"type": "text", "fontSize": 13, "fontWeight": 700, "color": "#1d1712",
                 "baseline": "middle", "dx": {"expr": "datum.align == 'left' ? 4 : -4"},
                 "align": {"expr": "datum.align"}},
        "encoding": {"longitude": {"field": "lon", "type": "quantitative"},
                     "latitude": {"field": "lat", "type": "quantitative"},
                     "text": {"field": "t"}}
    },
]

def is_old_label(layer):
    vals = layer.get("data", {}).get("values", [])
    return any("inset" in str(v.get("label", "")) or "zoomed" in str(v.get("label", "")) or "▸" in str(v.get("label", ""))
               for v in vals if isinstance(v, dict))

old = [i for i, l in enumerate(main["layer"]) if is_old_label(l)]
if old:
    i = old[0]
    main["layer"][i:i + 1] = new_layers
    print("Year 12 map: city boxes, leader lines and labels added.")
else:
    print("Year 12 map: city boxes already there - skipped.")

# clip every map shape to the frame, so islands outside it (Lord Howe, Torres Strait)
# are not drawn floating outside the ocean background
for layer in main["layer"]:
    m = layer.get("mark")
    if isinstance(m, dict) and m.get("type") == "geoshape":
        m["clip"] = True
spec_path.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n")

# Two-line map annotations ("Lowest completion:|remote Northern Territory" etc.):
# lift both lines above the leader line's starting point so the dashed line
# no longer runs through the second line of text. Applies to maps 01, 06 and 09.
def lift(node):
    changed = 0
    if isinstance(node, dict):
        m = node.get("mark")
        if isinstance(m, dict) and m.get("type") == "text" and m.get("lineBreak") == "|" \
                and m.get("baseline") == "bottom" and m.get("dy") != -24:
            m["dy"] = -24
            changed += 1
        for v in node.values():
            changed += lift(v)
    elif isinstance(node, list):
        for v in node:
            changed += lift(v)
    return changed

for name in ["01_map_bivariate.vl.json", "06_map_schools_strip.vl.json", "09_map_year12.vl.json"]:
    p = ROOT / "specs" / name
    s = json.loads(p.read_text())
    n = lift(s)
    p.write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n")
    print(f"{name}: {n} annotation(s) lifted above the leader line")

# remove the duplicated subtitle sentence(s) from index.html
html_path = ROOT / "index.html"
html = html_path.read_text()
html2 = re.sub(r"\s*Right: Sydney and Melbourne zoomed in\.", "", html)
html_path.write_text(html2)

print("index.html: subtitle lines removed:", html.count("Right: Sydney and Melbourne zoomed in."))
