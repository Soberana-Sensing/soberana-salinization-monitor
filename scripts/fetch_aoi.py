"""Fetch Casamance AOI boundaries from geoBoundaries gbOpen SEN ADM1.

Writes data/aoi/basse-casamance.geojson (Ziguinchor) and data/aoi/casamance.geojson
(Ziguinchor, Sedhiou, Kolda). Idempotent: overwrites with the same pinned release.
"""

from __future__ import annotations

import json
from pathlib import Path

import requests

API = "https://www.geoboundaries.org/api/current/gbOpen/SEN/ADM1/"
OUT = Path(__file__).resolve().parents[1] / "data" / "aoi"
PHASE1 = {"Ziguinchor"}
CASAMANCE = {"Ziguinchor", "Sedhiou", "Kolda"}
PROPS = {
    "source": "geoBoundaries gbOpen SEN ADM1, boundaryYearRepresented 2019, build 2023-12-12",
    "licence": "CC BY 3.0 IGO",
}


def download(url: str) -> dict:
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    text = resp.text.lstrip()
    if text.startswith("version https://git-lfs"):
        # GitHub serves the pointer from raw; LFS media host serves the payload.
        url = url.replace("raw.githubusercontent.com", "media.githubusercontent.com/media")
        resp = requests.get(url, timeout=120)
        resp.raise_for_status()
    return resp.json()


def subset(source: dict, names: set[str]) -> dict:
    features = []
    for feature in source["features"]:
        if feature["properties"]["shapeName"] in names:
            features.append(
                {
                    "type": "Feature",
                    "properties": {
                        "name": feature["properties"]["shapeName"],
                        "iso": feature["properties"].get("shapeISO"),
                        **PROPS,
                    },
                    "geometry": feature["geometry"],
                }
            )
    missing = names - {f["properties"]["name"] for f in features}
    if missing:
        raise RuntimeError(f"missing boundaries: {sorted(missing)}")
    return {"type": "FeatureCollection", "features": features}


def main() -> None:
    meta = requests.get(API, timeout=60).json()
    source = download(meta["simplifiedGeometryGeoJSON"])
    OUT.mkdir(parents=True, exist_ok=True)
    for filename, names in (
        ("basse-casamance.geojson", PHASE1),
        ("casamance.geojson", CASAMANCE),
    ):
        path = OUT / filename
        path.write_text(json.dumps(subset(source, names), indent=1), encoding="utf-8")
        print(f"wrote {path} ({len(names)} region(s))")


if __name__ == "__main__":
    main()
