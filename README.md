# Soberana Salinization Monitor

Map and monitor soil salinization from free satellite data, and serve the result as a dashboard.
Area of interest for the first phase: the Casamance, southern Senegal. The estuary and its
lowlands are the core; the wider Casamance (Ziguinchor, Sédhiou, Kolda regions) is the eventual
coverage.

Status: scaffold, created 2026-11-18. No method validated, no map published, no dashboard beyond
a placeholder. The plan lives in `docs/PLAN.md` and binds once written.

## Why Casamance

Salinization in Casamance is a documented, ongoing land-degradation process, not a hypothetical
risk.

- Senegal counts about 1.7 million hectares of salt-affected soil, near 45 % of its arable land
  (Bureau pédologique, Direction de l'Agriculture, 1997 estimate). The Casamance basin alone is
  put at 400,000 ha (Sadio 1991). Both figures are cited in Sané 2023.
- The driver is the rainfall break after 1967: the mean annual rainfall at Ziguinchor fell from
  1577 mm over 1921–1967 to 1148 mm over 1968–1988. Lower freshwater input let the marine salt
  wedge move upstream, and the water table dropped. Salt then concentrated in the topsoil during
  the seven to eight dry months and was no longer flushed in the wet season (Mougenot, ORSTOM,
  1996).
- Mangrove soils carry sulfidic material. Once exposed by sustained drainage they oxidize and pH
  can fall from about 7 to about 3, turning mangrove and former rice land into bare hypersaline
  `tannes` (Mougenot 1996). Salinity and acidity are therefore two different hazards with different
  signatures, and a single "salt" class would blur them.
- Rice land is the visible casualty. In the Diouloulou watershed, cultivated rice fields declined
  by 1.17 % per year, plateau crops by 0.68 % and mangrove by 1.04 % over the study period, with
  abandoned fields replaced by tannes (Sané 2023).
- Anti-salt dikes and micro-dams are the main adaptation, built across the lowlands over the past
  decades. Their condition varies, so the landscape carries both protected and unprotected
  lowlands.

## What the tool should do

1. Map salinity state at field-relevant resolution (10 m Sentinel-2 grid, 30 m where Landsat
   history is needed), as classes rather than a bare continuous index.
2. Separate saline from acid-sulfate-affected ground, since the management response differs.
3. Track change over the Sentinel-2 era (2015-06-23 onward) and, at coarser confidence, over the
   Landsat era (1984 onward).
4. Show the drivers that make a map actionable: proximity to the estuary and tidal creeks, surface
   water, mangrove extent, dike infrastructure where data exists, rainfall of the preceding wet
   season.
5. Serve all of it as a dashboard: layer toggles, time slider, class legend, uncertainty, and a
   download for the polygons behind a click.

The honest constraint: optical salinity indices are proxies. Surface salt, moisture, texture and
vegetation all move the same bands. Published Senegalese work reaches R² 0.73 for EC in the Saloum
(Djilor, 300 topsoil samples, Landsat 2017) and 0.94–0.98 overall accuracy for saline-soil classes
with Sentinel-2 plus Sentinel-1 in the northern Saloum estuary. Those numbers come from other
estuaries and do not transfer to Casamance without local labels. Validation with field electrical
conductivity is the gate, not an optional extra.

## Method direction

Sentinel-2 L2A surface reflectance, dry-season and wet-season composites, screened with the scene
classification layer. Salinity and brightness indices (SI, SI2, NDSI, BSI, NDVI, SAVI), plus
Sentinel-1 C-band backscatter for surface roughness and moisture, plus a DEM for elevation and
distance-to-water terms. Classifier candidates: random forest and gradient boosting, with the
published Saloum result as the reference design (Sentinel-1 alone is weak, around 0.62–0.67
overall accuracy; the optical stack carries the discrimination).

SoilGrids and iSDAsoil are not usable as salinity priors: neither product maps electrical
conductivity or salts, so there is nothing to ingest. They remain useful for texture and drainage
context.

## Layout

| Path | Content |
|------|---------|
| `app/` | Streamlit dashboard |
| `data/aoi/` | area-of-interest boundaries, tracked |
| `data/raw/` | data as delivered, git-ignored |
| `data/interim/` | reshaped intermediates, git-ignored |
| `data/derived/` | analysis outputs, git-ignored |
| `docs/` | plan, data inventory, licensing |
| `notebooks/` | exploration |
| `scripts/` | fetch and processing entry points |

## Run the dashboard

```bash
python -m venv soberana-salinization-monitor-venv
source soberana-salinization-monitor-venv/bin/activate
pip install -r requirements.txt
streamlit run app/main.py
```

The scaffold renders the Casamance boundaries and a data-inventory panel. Layers appear as
products land in `data/derived/`.

## Data dates

Every dataset carries its date: acquisition window, product epoch, or retrieval date. The current
inventory is in `docs/DATA.md`.

## Licence

Code: Apache-2.0 (`LICENSE`). Data, documentation and map products: CC BY 4.0. Third-party data
keeps its own licence, listed per source in `docs/DATA.md`. See `docs/LICENSING.md`.
