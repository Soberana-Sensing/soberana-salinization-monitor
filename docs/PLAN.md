# Plan — salinization mapping and monitoring, Casamance

Status: draft, 2026-11-18. Binds once the owner approves it. Nothing here is a result.

## 1. Question the product answers

For each lowland unit in the Casamance, what is the current salinity state, is it acid-sulfate
affected, and how has it moved since the satellite record began? The user of the answer is a
land-use decision maker: a farmer organisation, an extension service, an NGO running dike
rehabilitation. A pixel class is only useful if it survives a field check, so the plan is built
around validation rather than around index beauty.

## 2. Area of interest

- Phase 1: Ziguinchor region (Basse-Casamance), the estuary and its immediate lowlands.
  Boundary: `data/aoi/basse-casamance.geojson`, geoBoundaries gbOpen SEN ADM1
  (boundaryYearRepresented 2019, build 2023-12-12, CC BY 3.0 IGO).
- Phase 2: Sédhiou and Kolda added, the full Casamance administrative extent:
  `data/aoi/casamance.geojson`.
- Working grid: UTM zone 28N (EPSG:32628) for analysis, EPSG:4326 for display, and an equal-area
  projection for any hectare figure. Never quote area computed in Web Mercator.

The lowland mask matters more than the region boundary. Slopes are very small in the fluvio-marine
domain, and the saline hazard is confined to land below a few metres and near tidal water. Mask by
elevation, distance to estuary and tidal creeks, and the mangrove history.

## 3. Salinity classes

Electrical conductivity of the saturated paste extract, topsoil 0–30 cm, in dS/m at 25 °C:

| Class | EC (dS/m) | Label |
|-------|-----------|-------|
| 0 | 0–2 | non-saline |
| 1 | 2–4 | slightly saline |
| 2 | 4–8 | moderately saline |
| 3 | 8–16 | strongly saline |
| 4 | >16 | extremely saline |

Thresholds follow the standard USDA/NRCS division. The same breakpoints appear in the Senegalese
salinity literature, which keeps our classes comparable to published maps.

Acid sulfate status is a separate axis, not a class in the same scale: `none`, `potential`
(sulfidic material below the surface), `actual` (pH under about 4 after oxidation, jarosite or
yellow mottles visible). Surface pH is not derivable from optical imagery alone; the working
assumption is that bare hypersaline tannes with a known mangrove history are the candidates, and
the map says `potential` until a field pH confirms it.

## 4. Products

1. **State map**, dry season of the latest complete hydrological year: salinity class,
   per-pixel confidence, acid-sulfate flag. Vectorised to polygons with a minimum mapping unit of
   0.5 ha so the dashboard does not show speckle.
2. **Change layer**: class transitions between epochs, both directions. Protection by dikes should
   show as stable or recovering; unprotected lowlands as progression. Any claim of recovery needs
   two dates and a field check.
3. **Driver context**: distance to estuary and tidal creeks, elevation, mangrove extent history,
   surface water occurrence, rainfall anomaly of the preceding wet season, dike locations where a
   source can be licensed.
4. **Dashboard**: layer toggles, epoch selector, class legend, confidence shading, click for
   polygon attributes, CSV/GeoJSON download, and a methodology page that states the limits in
   plain language.

Seasonality is part of the product, not noise. Dry-season composites show the salt crust best;
wet-season composites show whether the salt is flushed. Ship both, labelled.

## 5. Method

### 5.1 Inputs

Full inventory with dates and licences in `docs/DATA.md`. Short version: Sentinel-2 L2A
(2015-06-23 onward, 10–20 m), Sentinel-1 GRD (2014-10 onward, C-band), Landsat 5/7/8/9
(1984 onward, 30 m), Copernicus DEM GLO-30, CHIRPS rainfall, JRC Global Surface Water, Global
Mangrove Watch, geoBoundaries.

### 5.2 Predictors

- Sentinel-2 bands B02, B03, B04, B08, B11, B12.
- Indices: SI, SI2, NDSI, BSI, NDVI, SAVI, MNDWI, plus green/SWIR and red/SWIR ratios. The Saloum
  study used NDSI, NDWI, NDVI and ratios; the Djilor study used SI, NDVI, SAVI with elevation and
  distance to river.
- Sentinel-1 VV and VH backscatter statistics (median, and a dry-season composite), plus VV/VH
  ratio. Radar adds roughness and moisture structure that optical indices confuse with salt.
- Terrain: elevation, slope, topographic wetness index, distance to estuary, distance to nearest
  tidal creek.
- Context: land cover class from the optical stack, mangrove history flag, dike proximity.

### 5.3 Model

Start with a published-design replication: random forest on the full stack, trained on field EC
labels, validated with spatially blocked folds. Compare against gradient boosting and against a
regression-kriging variant. Report overall accuracy, per-class precision and recall, and the
confusion between saline bare soil, mudflat and senescent mangrove, which is where the Saloum work
found its residual error.

Order of work: univariate index screening first (which index tracks EC at all in Casamance), then
the multivariate classifier, then change detection. Do not skip the screening step; published
R² values come from other estuaries.

Uncertainty: per-class probability from the ensemble, plus a validation-based interval on class
area. A class map without an uncertainty layer is not shipped.

### 5.4 Change detection

Two epochs minimum, same season, same sensor family. Direct classification comparison plus a
transition matrix. Cross-sensor comparisons (Landsat to Sentinel-2) are flagged as lower
confidence. The Sentinel-1 record extends the change window through cloud, but only after the
optical model is validated.

### 5.5 Validation

This is the binding constraint. There is no open, georeferenced EC dataset for Casamance that we
have found. Options, in order:

1. Partnership with a Senegalese institution that holds field data: ISRA, the Ziguinchor
   geography laboratories (UASZ, LGE), or an NGO running dike rehabilitation. Request with a
   defined sampling design, not a data dump.
2. Own field campaign: topsoil EC (1:5 or saturated paste, stated), pH, and a GPS point per
   sample, stratified by suspected class. Minimum viable set is around 150–200 points for a
   five-class map; the Djilor study used 300.
3. Literature points: extract georeferenced sample locations from published Casamance studies,
   with sampling dates, and treat them as a separate, weaker validation set. Citation required,
   re-use licence checked.

Contamination rule, carried over from the soil project: no record sampled before 2021 is used as
independent validation for a map product trained on legacy data, and points inside a training set
are never used as evidence. For salinity the risk is lower because SoilGrids and iSDAsoil do not
map EC, but the rule stays for any future prior.

## 6. Dashboard

Python, Streamlit, rasterio/rioxarray for the raster side, GeoPandas for vectors, pydeck for the
map. Static layers precomputed into Cloud-Optimised GeoTIFF or GeoParquet; the app never streams
raw scenes. Deployment target: a small container, publicly reachable, no login for the public
layers.

Panels: map, epoch selector, class legend, area statistics per commune, time series for a clicked
polygon, methodology and limits page, download.

## 7. Sequence

1. Boundary and lowland mask (done in scaffold for boundaries).
2. Sentinel-2 dry- and wet-season composites for Ziguinchor, 2016–2026, with cloud and tide
   screening.
3. Index screening against whatever labels can be secured, plus a visual audit on known tannes.
4. Classifier with blocked cross-validation.
5. Field validation round, then map revision.
6. Change layer over the Sentinel-2 era.
7. Dashboard built against real products, not placeholders.

## 8. Risks

- **Labels**: the whole product rests on field EC. Without a partner or a campaign, the map is an
  index map with a confidence claim we cannot support. Say so before anyone downstream plans on it.
- **Confusion between salt crust, mudflat and dead mangrove.** Mitigate with Sentinel-1, texture,
  and mangrove history; report it in the confusion matrix rather than hiding it.
- **Tides**: the estuary is tidal. Acquisition time relative to tide changes surface moisture and
  therefore the signal. Screen with tide phase where a harmonic model is available, and prefer
  composites that mix tidal states rather than single dates.
- **Acid sulfate soils** may be misread as salinity. Keep the two axes separate and label the acid
  flag as potential until pH data exists.
- **Rainfall variability**: a single dry year can look like a trend. Always plot the rainfall
  anomaly beside the change map.
- **Area claims**: use an equal-area projection for hectares; Web Mercator inflates this latitude
  by roughly a third.

## 9. Open decisions

- Phase 1 extent: Ziguinchor region only, or all three Casamance regions at coarser confidence?
- Validation route: partner data request first, or plan a field campaign in the 2026–2027 dry
  season?
- Acid sulfate handling: separate product, or a flag on the salinity map?
- Dashboard hosting: internal demo first, or public from the first map?
- Dike inventory: is there a licensable georeferenced source, or does it stay out of scope?
