#!/usr/bin/env python3
"""
Fetch real Toronto street + building data from OpenStreetMap's Overpass API and
convert it into a compact local-metre JSON blob the game loads with zero runtime
map dependencies.

Covers the WHOLE playable map: Rogers Centre / Roundhouse in the west to
St. Lawrence Market / Jarvis St in the east, the lakeshore to north of King St.

Output: ../toronto_map.js  (defines window.TORONTO_MAP)

Usage:
  python3 tools/fetch_toronto.py                  # download + write toronto_map.js
  python3 tools/fetch_toronto.py --save-raw raw.json   # also keep the raw Overpass reply
  python3 tools/fetch_toronto.py --input raw.json      # rebuild offline from a saved reply

Map data (c) OpenStreetMap contributors, ODbL. Attribution is shown in-game.
"""
import argparse
import json
import math
import os
import sys
import urllib.parse
import urllib.request

# Data bounding box (S, W, N, E). Matches the game's map bounds exactly, so every
# street the player can reach has real buildings along it.
S, W, N, E = 43.63932, -79.39368, 43.65012, -79.37133

# Projection origin (between CN Tower and Union Station) -- do not change, all
# game coordinates are relative to this point.
LAT0, LON0 = 43.6440, -79.3835
M_PER_DEG_LAT = 111_132.0
M_PER_DEG_LON = 111_320.0 * math.cos(math.radians(LAT0))

ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://z.overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

QUERY = f"""
[out:json][timeout:180];
(
  way["building"]({S},{W},{N},{E});
  relation["building"]({S},{W},{N},{E});
  way["highway"]({S},{W},{N},{E});
  way["railway"="rail"]({S},{W},{N},{E});
);
out geom tags;
"""

ROAD_WIDTHS = {
    "motorway": 14, "motorway_link": 7, "trunk": 14, "trunk_link": 7,
    "primary": 13, "primary_link": 7, "secondary": 11, "secondary_link": 6,
    "tertiary": 9, "tertiary_link": 6, "residential": 7, "unclassified": 7,
    "living_street": 6, "service": 5, "pedestrian": 6,
}

# Landmarks the game models by hand. Position = centroid of the real OSM footprint
# whose name matches; the lat/lon is only a fallback if OSM doesn't have it.
LANDMARKS = {
    "cnTower":      (["CN Tower"],                                   43.642566, -79.387057),
    "unionStation": (["Union Station"],                              43.645541, -79.380648),
    "rogersCentre": (["Rogers Centre"],                              43.641438, -79.389353),
    "ripleys":      (["Ripley's Aquarium"],                          43.642458, -79.386189),
    "roundhouse":   (["John Street Roundhouse"],                     43.640855, -79.386031),
    "royalYork":    (["Fairmont Royal York"],                        43.645936, -79.381288),
    "royThomson":   (["Roy Thomson Hall"],                           43.646632, -79.386343),
    "pecautSquare": ([],                                             43.646160, -79.386541),
    "gooderham":    (["Gooderham Building"],                         43.648400, -79.374500),
    "stLawrence":   (["St. Lawrence Market South", "St. Lawrence Market"], 43.648769, -79.373010),
}


def proj(lat, lon):
    x = (lon - LON0) * M_PER_DEG_LON
    z = -(lat - LAT0) * M_PER_DEG_LAT  # north = -Z (three.js forward)
    return round(x, 1), round(z, 1)


def parse_height(tags):
    h = tags.get("height") or tags.get("building:height")
    if h:
        try:
            return float(str(h).replace("m", "").split(";")[0].strip())
        except ValueError:
            pass
    lv = tags.get("building:levels")
    if lv:
        try:
            return float(str(lv).split(";")[0]) * 3.6 + 2
        except ValueError:
            pass
    return None


def flat(coords):
    out = []
    for x, z in coords:
        out.extend([x, z])
    return out


def fetch():
    data = urllib.parse.urlencode({"data": QUERY}).encode()
    last_err = None
    for url in ENDPOINTS:
        try:
            print(f"Querying {url} ...", file=sys.stderr)
            req = urllib.request.Request(url, data=data, headers={"User-Agent": "fist-of-doom-toronto/1.1"})
            with urllib.request.urlopen(req, timeout=240) as r:
                return json.loads(r.read().decode())
        except Exception as e:  # noqa: BLE001
            last_err = e
            print(f"  failed: {e}", file=sys.stderr)
    raise SystemExit(f"All Overpass endpoints failed: {last_err}")


def centroid(pts):
    return sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)


def area(pts):
    a = 0.0
    for i in range(len(pts)):
        x0, z0 = pts[i]
        x1, z1 = pts[(i + 1) % len(pts)]
        a += x0 * z1 - x1 * z0
    return abs(a) / 2


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", help="build from a saved Overpass JSON reply instead of downloading")
    ap.add_argument("--save-raw", help="also save the raw Overpass reply to this file")
    args = ap.parse_args()

    if args.input:
        with open(args.input, encoding="utf-8") as f:
            raw = json.load(f)
    else:
        raw = fetch()
        if args.save_raw:
            with open(args.save_raw, "w", encoding="utf-8") as f:
                json.dump(raw, f)

    buildings, roads, rails = [], [], []
    named_feet = []  # (name, centroid, area) for landmark lookup

    for el in raw.get("elements", []):
        tags = el.get("tags", {})
        polys = []
        if el["type"] == "way" and "geometry" in el:
            polys = [el["geometry"]]
        elif el["type"] == "relation":
            for m in el.get("members", []):
                if m.get("role") == "outer" and "geometry" in m:
                    polys.append(m["geometry"])

        if "building" in tags:
            h = parse_height(tags)
            for g in polys:
                pts = [proj(p["lat"], p["lon"]) for p in g]
                if len(pts) > 1 and pts[0] == pts[-1]:
                    pts = pts[:-1]
                if len(pts) < 3:
                    continue
                b = {"p": flat(pts)}
                if h:
                    b["h"] = round(h, 1)
                name = tags.get("name")
                if name:
                    b["n"] = name
                    named_feet.append((name, centroid(pts), area(pts)))
                buildings.append(b)

        elif "highway" in tags and el["type"] == "way":
            hw = tags["highway"]
            if hw not in ROAD_WIDTHS or tags.get("tunnel") in ("yes", "building_passage"):
                continue
            if tags.get("area") == "yes":
                continue
            pts = [proj(p["lat"], p["lon"]) for p in el["geometry"]]
            r = {"t": hw, "w": ROAD_WIDTHS[hw], "p": flat(pts)}
            if tags.get("bridge") == "yes":
                try:
                    r["l"] = max(1, int(tags.get("layer", "1")))
                except ValueError:
                    r["l"] = 1
            if tags.get("name"):
                r["n"] = tags["name"]
            roads.append(r)

        elif tags.get("railway") == "rail" and el["type"] == "way":
            if tags.get("tunnel") == "yes":
                continue
            pts = [proj(p["lat"], p["lon"]) for p in el["geometry"]]
            rails.append({"p": flat(pts)})

    # Landmarks: centroid of the largest real footprint whose name matches
    landmarks, report = {}, []
    for key, (names, lat, lon) in LANDMARKS.items():
        found = None
        for wanted in names:
            hits = [f for f in named_feet if f[0].startswith(wanted)]
            if hits:
                found = max(hits, key=lambda f: f[2])
                break
        if found and key != "cnTower":
            landmarks[key] = [round(found[1][0], 1), round(found[1][1], 1)]
            report.append(f"{key}: from OSM footprint '{found[0]}'")
        else:
            landmarks[key] = list(proj(lat, lon))
            report.append(f"{key}: fixed coordinates" + ("" if key in ("cnTower", "pecautSquare") else "  (WARNING: no OSM footprint found)"))

    out = {
        "attribution": "Map data \u00a9 OpenStreetMap contributors (ODbL)",
        "origin": [LAT0, LON0],
        "bounds": [proj(N, W), proj(S, E)],
        # Area actually covered by real OSM data. The game only invents filler
        # buildings OUTSIDE this box (distant skyline beyond the playable area).
        "dataBounds": [proj(N, W), proj(S, E)],
        "landmarks": landmarks,
        "buildings": buildings,
        "roads": roads,
        "rails": rails,
    }

    here = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(here, "..", "toronto_map.js")
    with open(target, "w", encoding="utf-8") as f:
        f.write("// Auto-generated by tools/fetch_toronto.py\n")
        f.write("// Map data (c) OpenStreetMap contributors, ODbL 1.0. https://www.openstreetmap.org/copyright\n")
        f.write("window.TORONTO_MAP = ")
        json.dump(out, f, separators=(",", ":"), ensure_ascii=False)
        f.write(";\n")

    with_h = sum(1 for b in buildings if "h" in b)
    print(f"buildings={len(buildings)} (with real height: {with_h}) roads={len(roads)} rails={len(rails)} "
          f"size={os.path.getsize(target)//1024}KB", file=sys.stderr)
    print("landmarks:\n  " + "\n  ".join(report), file=sys.stderr)


if __name__ == "__main__":
    main()
