# Plan — salinization mapping and monitoring, Lower Casamance

Status: draft, revised 2026-11-18. Binds once the owner approves it. Nothing here is a result.

## 1. Question the product answers

For each lowland unit in the Lower Casamance, what is the salt state of the topsoil and the
subsoil, what is the probability that it exceeds a given salinity threshold, and which units carry
the paddy, mangrove and tidal-creek context that makes salt a live constraint on land use?

The user of the answer is a land-use decision maker: a farmer organisation, an extension service,
an NGO running dike rehabilitation. That user acts on a probability and a class, not on a
continuous index, so every shipped layer carries an exceedance probability and a class, and no
layer ships without a stated measurement basis.

**Product label, fixed.** The static product is a *prior-conditioned salinity risk indicator*. It
carries no accuracy number and no trend claim. The word "monitoring" is not used for any layer
until a georeferenced ECe observation set dated 2021 or later exists. Until then the dashboard
says "risk indicator, unvalidated", in those words.

## 2. Area of interest

- Extent: Lower Casamance, defined as the union of three geoBoundaries gbOpen SEN ADM2 units —
  Bignona, Oussouye, Ziguinchor. Not a hand-drawn bounding box. The boundary file is fetched,
  registered, and resolved by the slug `casamance`.
- Current state: `data/aoi/basse-casamance.geojson` holds the ADM1 Ziguinchor region,
  boundaryYearRepresented 2019, build 2023-12-12, CC BY 3.0 IGO, fetched 2026-11-18. The ADM2
  union replaces it as the working extent in phase 0.
- Working grid: UTM zone 28N (EPSG:32628) for analysis, EPSG:4326 for display, and an equal-area
  projection for any hectare figure. Never quote area computed in Web Mercator.
- The lowland mask does the work the boundary cannot. The saline hazard is confined to the
  fluvio-marine lowland, so the dynamic layers are clipped to a tidal lowland mask built from
  elevation band, distance to the marigot network, and mangrove plus paddy land-cover class. The
  static layers keep the full department union, so the lowland mask is visible as a layer rather
  than silently baked in.

## 3. Measurement basis and classes

**Delivered quantity:** electrical conductivity of the saturated paste extract, ECe, in dS/m at
25 °C, for 0–30 cm and 30–100 cm.

**Observation basis:** the 1:5 soil-to-water extract, because that is what Casamance laboratories
report. Published values from the Bignona and Mlomp studies run 0.01–9.77 mS/cm on that basis.
Every delivered ECe figure therefore carries its 1:5 basis beside it.

The 1:5 to ECe conversion is **not** one global factor. It is a fitted, texture-dependent offset.
With no paired 1:5 and ECe samples in hand, the conversion enters as a literature interval per
texture class, flagged in the metadata and widened into the posterior. When paired samples arrive,
the interval is replaced by a fitted relation and the revision is recorded.

Classes on ECe, topsoil 0–30 cm, dS/m at 25 °C:

| Class | ECe (dS/m) | Label |
|-------|------------|-------|
| 0 | 0–2 | non-saline |
| 1 | 2–4 | slightly saline |
| 2 | 4–8 | moderately saline |
| 3 | 8–16 | strongly saline |
| 4 | >16 | extremely saline |

Thresholds follow the USDA/NRCS division. The same breakpoints appear in the Senegalese salinity
literature, which keeps our classes comparable to published maps. Exceedance probabilities are
reported at 2, 4 and 8 dS/m, matching the class boundaries a decision maker acts on.

Acid sulfate status is a separate axis, not a class in the same scale: `none`, `potential`
(sulfidic material below the surface), `actual` (pH under about 4 after oxidation, jarosite or
yellow mottles visible). Surface pH is not derivable from optical imagery alone, and pH 3.2–4.6
occurs in the same bolanha as the saline soils. An EC-only answer will point a farmer at the wrong
intervention, so the acid flag travels with every polygon and the method page states the limit.
The map says `potential` until a field pH confirms it.

## 4. Products

1. **Static ECe baseline, 1 km.** Posterior mean ECe for 0–30 cm and 30–100 cm, exceedance
   probability P(ECe>2), P(ECe>4), P(ECe>8), FAO class, and a per-pixel uncertainty layer. Prior
   stack is GSASmap v1.0 plus HWSD v2 where an ECe layer exists for Senegal; covariates are
   iSDAsoil and SoilGrids. Label: prior-conditioned salinity risk indicator.
2. **Static risk view, 30 m.** The same product at the resolution the covariates support, carrying
   the risk label harder, because the 1 km prior is not resampled into a claim of 30 m knowledge.
3. **Soil moisture layer, 30 m.** A hard prerequisite for the joint state product, not an optional
   extra. Salt without water state cannot be separated from water state itself.
4. **Joint salt–moisture state, 30 m, monthly.** Mass balance driven by Sentinel-1 inundation
   frequency, tide stage, rainfall and evapotranspiration, with dry-season Sentinel-2 indices as
   observations. This is the only layer that may be called monitoring, and only once a 2021-or-later
   ECe observation set exists to anchor it.
5. **Jump alerts.** New inundation or new bare-soil patches relative to the previous stable state,
   reported as candidate events with the rainfall anomaly beside them, never as a confirmed trend.
6. **Dashboard.** Every layer carries its epoch, method, licence, revision date and band
   components, plus the 1:5 basis where ECe is shown. Static risk view at 1 km, monthly state view
   at 30 m, alerts, offline export of the layers the user is looking at.

Seasonality is part of the product, not noise. Dry-season composites show the salt crust; wet-season
composites show whether the salt is flushed. Ship both, labelled, and never let one stand in for the
other.

## 5. Method

### 5.1 Inputs

Full inventory with dates and licences in `docs/DATA.md`. Short version: GSASmap v1.0 national
summary (raster pending a data request), HWSD v2 pending verification, iSDAsoil 30 m, SoilGrids
250 m, DeltaDTM v1.1 at 30 m for terrain, Sentinel-2 L2A (2015-06-23 onward), Sentinel-1 GRD
(2014-10 onward), Landsat 5/7/8/9 (1984 onward), ERA5-Land for rainfall and ET context, CHIRPS for
rainfall anomaly, a tide or stage record for the estuary, JRC Global Surface Water, Global Mangrove
Watch, geoBoundaries.

### 5.2 Static baseline

Bayesian, because the priors are of mixed vintage and the labels do not exist yet.

- Observations: GSASmap v1.0 salt-affected area at 1 km if the raster is released; the Annex 3
  national total as an aggregate constraint meanwhile; HWSD v2 ECe where it covers Senegal.
  Treated as a vintage mixture with an explicit `t_0` per source, not as contemporaneous truth.
- Covariates: iSDAsoil texture, pH and drainage context at 30 m; SoilGrids 250 m for the same;
  terrain from DeltaDTM; distance to estuary and to marigot; mangrove history; surface water
  occurrence.
- Output: posterior mean, exceedance probability at the three thresholds, class, and uncertainty.
  The `sigma_method` term carries the 1:5 to ECe interval.

If no GSASmap raster is released and HWSD carries no usable ECe, the static product degrades to a
covariate-only risk index. That degradation is a shipped label change, not a footnote.

### 5.3 Moisture and joint state

- Moisture comes first. Sentinel-1 VV/VH statistics feed a surface-moisture estimate constrained by
  tidal stage and antecedent rainfall from ERA5-Land.
- Joint state is a mass balance: salt mass conserved in the lowland unit, water flux driven by
  inundation frequency, tide stage, rainfall and ET. Sentinel-2 dry-season indices enter as
  observations of surface expression, not as the state variable.
- Salt and water alias in the optical signal. The literature has not resolved it. Sequence moisture
  before salt so the ambiguity is bounded by a measured water state rather than guessed away.

### 5.4 Uncertainty and validation

Per-pixel posterior plus a literature-interval term per texture class for the 1:5 conversion. The
uncertainty layer is mandatory; a class map without it is not a product.

Validation remains the binding constraint, and there is no local validation today. The route is a
designed field campaign, not a data dump: stratified by tidal zone × land cover × class, paired dry
and wet season, 0–20 cm and 20–50 cm, ECe plus 1:5 plus pH plus texture, with a power calculation
and non-circular sampling. Gates 1–3 ship as "no local validation exists".

Contamination rule, carried over from the soil project: no record sampled before 2021 is used as
independent validation for a map product trained on legacy data, and points inside a training set
are never used as evidence. For salinity the risk is lower because SoilGrids and iSDAsoil do not
map EC, but the rule stays for every prior that does.

DEM vertical error is declared, not hidden. DeltaDTM carries a mean absolute error near 0.45 m; in
a lowland with slopes under 1 % that error is a real band in the inundation model, so it appears as
a band term and in the limits page.

## 6. Dashboard

Python, Streamlit, rasterio/rioxarray for the raster side, GeoPandas for vectors, pydeck for the
map. Static layers precomputed into Cloud-Optimised GeoTIFF or GeoParquet; the app never streams
raw scenes. Deployment target: a small container, publicly reachable, no login for public layers.

Panels: static ECe and risk map with class legend and exceedance layers, monthly state view, alerts,
epoch and revision selector, area statistics per commune, methodology and limits page, download.
Every panel shows the layer's epoch, method, licence and the 1:5 basis where ECe appears.

## 7. Sequence

0. **Phase 0 — extent, gates, access.** Fetch the SEN ADM2 boundary union (Bignona, Oussouye,
   Ziguinchor), register it, resolve the slug `casamance`. Check GSASmap v1.0 coverage for Senegal
   (done: present as a national figure, raster not open). Send the national raster request to the
   FAO GSP GSASmap team and to the INP as Senegal's INSII focal point. Verify HWSD v2 ECe for
   Senegal. Fix the DEM (done: DeltaDTM v1.1 replaces CoastalDEM). Identify the tide or stage
   source. Draft the partner data request to UASZ, ISRA and SODAGRI with the enrolment fields.
1. **Phase 1 — literature intake, cards only.** Casamance salinity and acidity papers (Bignona
   2020, Mlomp 2021, Djiguinoum 2025), Ivushkin 2019, the GSASmap method paper, mangrove and acid
   sulfate sources. One card per paper, router rows added. No full-text reading beyond the card.
2. **Phase 2 — fetch priors and covariates.** iSDA 30 m soil set, SoilGrids 250 m, GSASmap 1 km if
   released, Sentinel-1 2014–2026, Sentinel-2 dry-season composites 2015–2026, Landsat C2
   1984–2013, ERA5-Land, tide and stage, DeltaDTM crop. Registry row per file with date, licence,
   SHA-256. Volume expectation: one to four MGRS tiles, tens of GB.
3. **Phase 3 — static baseline at 1 km.** ECe latent field, prior mixture, posterior, exceedance,
   class, uncertainty. Ships under the risk label, with gates 1–3 satisfied as far as they can be
   without local labels.
4. **Phase 4 — soil moisture at 30 m.** Hard prerequisite, per §5.3.
5. **Phase 5 — joint salt–moisture state at 30 m.** Mass balance, monthly, alerts. The only layer
   that may be called monitoring, and only after a 2021-or-later ECe set exists.
6. **Phase 6 — field campaign design and execution.** Power calculation, stratified sample, paired
   seasons, ECe and 1:5 and pH and texture. This unblocks validation and the accuracy claim.
7. **Phase 7 — tool.** Static 1 km ECe and risk view, monthly 30 m state view, alerts, offline
   export, methodology page.

## 8. Risks

- **GSASmap raster access.** The national salt-affected area exists as a published figure; the 1 km
  raster is not on an open endpoint. If the request fails, the static product is covariate-only and
  is labelled as a risk index, not an ECe map.
- **GSASmap subsoil.** The Senegal 30–100 cm figure is 12.4 km² against 51 471.8 km² at 0–30 cm.
  That is neither physics nor a real depth signal; treat subsoil as absent for Senegal, never as low
  salinity at depth.
- **DEM error.** DeltaDTM is free and 30 m, which fixes availability, but 0.45 m mean absolute error
  on sub-1 % slopes bounds how far the inundation model can be trusted. Declare the band; do not
  refine it into a claim.
- **Salt versus water aliasing.** Unresolved in the literature. This is why moisture ships before
  salt, and why the joint state is a mass balance rather than an index stack.
- **Acid sulfate.** pH 3.2–4.6 in the same bolanha. An EC-only map points the farmer at the wrong
  fix; keep the acid axis on every polygon.
- **Mangrove inversion.** Green NDVI over hypersaline soil inverts the salinity sign. Vegetation
  indices alone are not evidence of low salinity; the mangrove history layer is mandatory context.
- **Confusion between salt crust, mudflat and dead mangrove.** Report it in the confusion matrix
  rather than hiding it, once there is a confusion matrix.
- **Tides.** Acquisition time relative to tide changes surface moisture and therefore the signal.
  Screen with tidal phase and prefer composites that mix tidal states over single dates.
- **Rainfall variability.** One dry year can look like a trend. Plot the rainfall anomaly beside any
  change or alert layer.
- **Area claims.** Equal-area projection for hectares; Web Mercator inflates this latitude by
  roughly a third.

## 9. Open decisions

- HWSD v2: does it carry ECe for Senegal at a usable resolution, and under what licence?
- Tide and stage source: which harmonic model or gauge record covers the Casamance estuary, and is
  it licensable?
- Validation route: partner data request first, or plan the field campaign for the 2026–2027 dry
  season in parallel?
- Dike inventory: is there a licensable georeferenced source, or does it stay out of scope?
- Dashboard hosting: internal demo first, or public from the first static product?
