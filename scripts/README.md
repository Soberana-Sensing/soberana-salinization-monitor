# scripts

One entry point per job. Every script states its inputs, its outputs and its date assumptions.

| Script | Job | Status |
|--------|-----|--------|
| `fetch_aoi.py` | download and subset the Casamance boundaries | works, boundary 2019, fetched 2026-11-18 |
| `fetch_sentinel2.py` | seasonal composites over the AOI | planned |
| `fetch_sentinel1.py` | backscatter composites over the AOI | planned |
| `build_predictors.py` | stack bands, indices, terrain and context into one table | planned |
| `classify.py` | train and validate the salinity classifier | planned |
| `change.py` | epoch comparison and transition matrix | planned |
| `export_dashboard.py` | COG and GeoParquet for the app | planned |

Fetches are dry-run by default where the source supports it, and never write into `data/` without
an explicit request.
