# data/aoi

Tracked area-of-interest boundaries. Small enough to version, and citable.

| File | Content | Source |
|------|---------|--------|
| `basse-casamance.geojson` | Ziguinchor region (ADM1), superseded as working extent | geoBoundaries gbOpen SEN ADM1, boundaryYearRepresented 2019, build 2023-12-12 |
| `casamance-low.geojson` | Lower Casamance: union of Bignona, Oussouye, Ziguinchor departments, working extent; not fetched yet, phase 0 | geoBoundaries gbOpen SEN ADM2, verify on fetch |
| `casamance.geojson` | Ziguinchor, Sédhiou, Kolda | geoBoundaries gbOpen SEN ADM1, boundaryYearRepresented 2019, build 2023-12-12 |

The working extent is the ADM2 union, resolver slug `casamance`. A hand-drawn bounding box is never
substituted for the boundary file.

Licence: CC BY 3.0 IGO (geoBoundaries). Fetch: `scripts/fetch_aoi.py`, retrieval date 2026-11-18.

Geometries are simplified. Do not use them for parcel-scale area figures; use them to clip
imagery and to frame the dashboard.
