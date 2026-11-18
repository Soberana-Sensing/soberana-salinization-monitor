# data/raw

Data as delivered, one folder per source: `raw/sentinel-2/`, `raw/sentinel-1/`, `raw/landsat/`,
`raw/dem/`, `raw/chirps/`, `raw/water/`, `raw/mangrove/`, `raw/boundaries/`.

Register every file in `REGISTRY.csv` (URL, retrieval date, licence, SHA-256). A fetch that writes
here needs an explicit request first.

Naming: `<source>/<extent>/<product>_<date-or-window>_<variable>.<ext>`, e.g.
`sentinel-2/ziguinchor/s2_dry-2025-2026_B04.tif`. Date always present.

Source list with licences: `docs/DATA.md`.
