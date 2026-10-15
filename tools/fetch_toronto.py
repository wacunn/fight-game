#!/usr/bin/env python3
"""
Fetch real Toronto street + building data (CN Tower / Union Station area)
from OpenStreetMap's Overpass API and convert it into a compact local-metre
JSON blob the game can load with zero runtime map dependencies.

Output: ../toronto_map.js  (defines window.TORONTO_MAP)

Map data (c) OpenStreetMap contributors, ODbL. Attribution is shown in-game.
"""
import json
import math
import os
import sys
import urllib.parse
import urllib.request

# Data bounding box (S, W, N, E): Union Station east edge -> past CN Tower / Rogers Centre
S, W, N, E = 43.6395, -79.3935, 43.6480, -79.3765

# Projection origin (between CN Tower and Union Station)
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
[out:json][timeout:90];
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
            req = urllib.request.Request(url, data=data, headers={"User-Agent": "fist-of-doom-toronto/1.0"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read().decode())
        except Exception as e:  # noqa: BLE001
            last_err = e
            print(f"  failed: {e}", file=sys.stderr)
    raise SystemExit(f"All Overpass endpoints failed: {last_err}")


def main():
    raw = fetch()
    buildings, roads, rails = [], [], []

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

    # Landmarks (projected)
    landmarks = {
        "cnTower": proj(43.642566, -79.387057),
        "unionStation": proj(43.645541, -79.380648),
        "rogersCentre": proj(43.641438, -79.389353),
    }

    out = {
        "attribution": "Map data \u00a9 OpenStreetMap contributors (ODbL)",
        "origin": [LAT0, LON0],
        "bounds": [proj(N, W), proj(S, E)],
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

    named = sorted({b["n"] for b in buildings if "n" in b})
    print(f"buildings={len(buildings)} roads={len(roads)} rails={len(rails)} "
          f"size={os.path.getsize(target)//1024}KB", file=sys.stderr)
    print("named buildings:", ", ".join(named[:60]), file=sys.stderr)


if __name__ == "__main__":
    main()
