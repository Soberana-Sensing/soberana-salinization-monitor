# Soberana Salinization Monitor

Map soil salinity from free satellite data, and serve the result as a dashboard. The extent is the
Lower Casamance, southern Senegal: the geoBoundaries ADM2 union of Bignona, Oussouye and Ziguinchor
departments, which contains the estuary and its lowlands. The wider Casamance (Sédhiou and Kolda
added) is a later coverage decision, not the first phase.

The delivered quantity is electrical conductivity of the saturated paste extract, ECe in dS/m, for
0–30 cm and 30–100 cm, with the 1:5 extract basis declared beside it, because Casamance laboratories
report 1:5 and the conversion to ECe is texture-dependent.

Status: scaffold, created 2026-11-18. No method validated, no map published, no dashboard beyond a
placeholder. The product on offer today is a prior-conditioned salinity risk indicator: no accuracy
number, no trend claim, and the word "monitoring" withheld until a georeferenced ECe observation set
dated 2021 or later exists. The plan lives in `docs/PLAN.md` and binds once written.

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

1. Map ECe at the resolution each data source supports: a 1 km static baseline from priors plus
   covariates, and a 30 m moisture and state layer where the satellite record carries the signal.
   Classes come with exceedance probabilities, not a bare continuous index.
2. Separate saline from acid-sulfate-affected ground, since the management response differs. The acid
   flag stays `potential` until a field pH confirms it.
3. Track change over the Sentinel-2 era (2015-06-23 onward) only after a 2021-or-later ECe dataset
   exists to anchor the state; the Landsat record (1984 onward) supports context, not a trend claim.
4. Show the drivers that make a map actionable: proximity to the estuary and tidal creeks, elevation,
   surface water, mangrove extent, dike infrastructure where data exists, rainfall of the preceding
   wet season.
5. Serve all of it as a dashboard: layer toggles, time slider, class legend, uncertainty, and a
   download for the polygons behind a click.

The honest constraint: optical salinity indices are proxies. Surface salt, moisture, texture and
vegetation all move the same bands. Published Senegalese work reaches R² 0.73 for EC in the Saloum
(Djilor, 300 topsoil samples, Landsat 2017) and 0.94–0.98 overall accuracy for saline-soil classes
with Sentinel-2 plus Sentinel-1 in the northern Saloum estuary. Those numbers come from other
estuaries and do not transfer to Casamance without local labels. Validation with field electrical
conductivity is the gate, not an optional extra.

## Method direction

Two stages, in this order.

**Static baseline.** A Bayesian ECe field at 1 km: GSASmap v1.0 as the national ECe prior, HWSD v2
where it carries ECe for Senegal, and iSDAsoil 30 m plus SoilGrids 250 m as covariates (texture, pH,
drainage). Published salt-affected area for Senegal exists (51 471.8 km² at 0–30 cm, 26.7 % of the
country, ECe > 2 dS/m, 1953–2020 average), but the 1 km raster is not on an open endpoint, so the
national raster is requested from FAO GSP and from INP as Senegal's INSII focal point. Output is a
posterior mean, P(ECe>2), P(ECe>4), P(ECe>8), FAO class, and an uncertainty layer.

**Moisture, then joint state.** Surface salt expression cannot be separated from surface moisture in
the optical signal, and the literature has not resolved the aliasing. So soil moisture at 30 m comes
first, driven by Sentinel-1 C-band statistics with tidal stage and ERA5-Land rainfall. The joint
salt–moisture state is then a mass balance forced by inundation frequency, tide stage, rainfall and
evapotranspiration, with dry-season Sentinel-2 indices as observations rather than as the state
variable. Optical indices used: SI, SI2, NDSI, BSI, NDVI, SAVI, MNDWI.

Terrain comes from DeltaDTM v1.1 (30 m, CC BY 4.0, mean absolute error 0.43–0.45 m). Copernicus
GLO-30 is kept as reference: its vertical error on sub-1 % slopes makes inundation modelling fiction,
and CoastalDEM's free tier is 90 m, which is worse. DeltaDTM's error is declared as a band term.

SoilGrids and iSDAsoil are not usable as salinity priors: neither product maps electrical
conductivity or salts, so there is nothing to ingest. They remain useful for texture and drainage
context, and texture sets the 1:5 to ECe conversion interval.

Validation stays the gate. No local ECe dataset exists, so the shipped static product is labelled a
risk indicator, and gates 1–3 of `AGENTS.md` are met as far as they can be without labels. The field
campaign is designed before it is run: stratified by tidal zone × land cover × class, paired dry and
wet season, 0–20 and 20–50 cm, ECe plus 1:5 plus pH plus texture.

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
