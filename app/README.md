# app

Streamlit dashboard. Run from the repo root:

```bash
streamlit run app/main.py
```

`main.py` reads boundaries from `data/aoi/` and the product inventory from `data/derived/`. It
holds no analysis code; products are precomputed by `scripts/` and exported as COG or GeoParquet.

State at 2026-11-18: placeholder. Map shows the AOI only. Panels for salinity class, acid sulfate
flag, mangrove history and surface water are disabled until a product exists.
