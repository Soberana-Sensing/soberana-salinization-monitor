# Data inventory

Every source carries its date, its resolution, its licence and its status. Retrieval dates are for
the scaffold sessions of 2026-11-18 unless stated otherwise. Nothing here is downloaded yet beyond
the area boundaries.

## Boundaries

| Source | Date represented | Access | Licence | Status |
|--------|------------------|--------|---------|--------|
| geoBoundaries gbOpen SEN ADM1 | boundaryYearRepresented 2019, build 2023-12-12, source update 2023-01-19 | `data/aoi/`, fetched 2026-11-18 via `scripts/fetch_aoi.py` | CC BY 3.0 IGO | in repo, superseded as working extent |
| geoBoundaries gbOpen SEN ADM2 | verify on fetch | union of Bignona, Oussouye, Ziguinchor; resolver slug `casamance` | CC BY 3.0 IGO | phase 0 fetch |

The working extent is the ADM2 union of the three Lower Casamance departments, not an ADM1 region
and not a hand-drawn bounding box. Phase 1 therefore drops the earlier Ziguinchor-region-only
scope: Bignona straddles the boundary the region lines draw, and the estuary system does not respect
it. Boundary positions are simplified geometries; for anything at parcel scale, replace with a
surveyed or national boundary source.

## Salinity priors

| Source | Date represented | Resolution | Licence | Status |
|--------|------------------|-----------|---------|--------|
| GSASmap v1.0, national summary for Senegal | long-term average 1953–2020, product published 2021 | national aggregate only | FAO GSP, cite the 2024 report | citable: 51 471.8 km² salt-affected at 0–30 cm (26.7 % of country), ECe > 2 dS/m; 12.4 km² at 30–100 cm |
| GSASmap v1.0, 1 km raster for Senegal | product year 2021, observation window 1953–2020 | 1 km | FAO GSP, request required | requested in phase 0 from FAO GSP and INP (INSII focal point) |
| HWSD v2 ECe, Senegal | verify on fetch | 1 km nominal | verify on fetch | unverified |

Two traps on the GSASmap numbers, both recorded here so they are not repeated downstream:

1. The raster is not on an open endpoint. The GloSIS catalogue holds GSAS mapsets for six countries
   only (PH, LA, VN, BD, MN, KH), all under the AFACI Asia programme; no Senegal mapset exists.
   Catalogue enumerated 2026-11-18, 145 mapsets. The global browser is a viewer, not a data service.
2. The 30–100 cm figure for Senegal is 12.4 km² against 51 471.8 km² in the topsoil. That is an
   empty or broken subsoil submission, not a physical result. Subsoil is treated as absent for
   Senegal; it is never read as low salinity at depth.

The 26.7 % is a national figure at ECe > 2 dS/m averaged over 1953–2020, and Casamance is one of
several national hotspots. It is not a Casamance number and is never quoted as one.

## Imagery

| Source | Coverage | Native resolution | Revisit | Licence | Status |
|--------|----------|-------------------|---------|---------|--------|
| Sentinel-2 L2A | 2015-06-23 onward | 10 m (B02, B03, B04, B08), 20 m (B11, B12), 60 m (SCL) | 5 days with both platforms | Copernicus, free and open | planned |
| Sentinel-1 GRD, C-band | 2014-10-03 onward | 10 m pixel, ~20 m resolution | 6–12 days per orbit | Copernicus, free and open | planned |
| Landsat 5 TM | 1984-03 to 2013-06 | 30 m | 16 days | USGS public domain | planned, historical change |
| Landsat 7 ETM+ | 1999-04 onward, scan-line gaps after 2003-05-31 | 30 m | 16 days | USGS public domain | planned, gap-tolerant only |
| Landsat 8 OLI/TIRS | 2013-04 onward | 30 m | 16 days | USGS public domain | planned |
| Landsat 9 OLI-2/TIRS-2 | 2021-10 onward | 30 m | 16 days | USGS public domain | planned |

Processing level for Sentinel-2: L2A surface reflectance, which is the analysis-ready product on
the Copernicus Data Space Ecosystem. Scene classification layer (SCL) does the cloud and shadow
screening.

## Terrain, water and vegetation context

| Source | Coverage represented | Resolution | Licence | Status |
|--------|----------------------|------------|---------|--------|
| DeltaDTM v1.1 | acquisitions 2012–2024, published 2024-12-12 | 30 m, mean absolute error 0.43–0.45 m | CC BY 4.0 | chosen; `Africa.zip` 2.78 GB, doi 10.4121/21997565, also Earth Engine `users/maartenpronk/deltadtm/v1-1` |
| Copernicus DEM GLO-30 | acquisitions 2011-01 to 2015-12, release 2021 | 30 m | Copernicus, free with attribution | superseded as terrain input, kept as reference |
| JRC Global Surface Water v1.4 | 1984-01 to 2021-12 | 30 m | Copernicus/JRC, free with attribution | planned |
| Global Mangrove Watch v3.0 | 1996 to 2020, 11 epochs | 25 m | CC BY 4.0 | planned |
| CHIRPS v2.0 daily rainfall | 1981-01 onward | 0.05° (~5.5 km) | public domain, CC0 | planned |
| ERA5-Land | verify on fetch (reanalysis through the present) | ~9 km, 0.1° | Copernicus CDS licence | planned |

DeltaDTM is a coastal-lowland product built by Deltares and TU Delft from Copernicus DEM corrected
with ICESat-2 and GEDI heights. Casamance relief stays below 30 m a.s.l., so coverage is complete
for the extent. Its mean absolute error of about 0.45 m is carried as an explicit band term in the
inundation model; on slopes under 1 % that error is material and is not refined away.

CoastalDEM v3.0 was checked and rejected: the no-cost tier is 90 m, non-commercial, by manual
application, and the 30 m product is a paid annual licence. At 90 m it is coarser than a free 30 m
model and buys nothing for tidal flats at this scale.

Tide and stage: no source fixed yet. The estuary is tidal and the surface signal depends on stage,
so a harmonic model or gauge record must be identified before the moisture layer is built. Open
decision in `docs/PLAN.md` §9.

## Soil context, with the reason each is not a salinity prior on its own

| Source | Date represented | Why it is here | Licence | Status |
|--------|------------------|----------------|---------|--------|
| iSDAsoil Africa 30 m | epoch 2001-01-01 to 2017-01-01, covariates Sentinel-2 2018–2019 percentiles | texture, pH, drainage context; no EC, no salt content | CC BY 4.0 | candidate |
| SoilGrids 2.0 250 m | WoSIS snapshot 2020-01, covariate windows 2001–2015 | texture, bulk density, drainage context; no EC | CC BY 4.0 | candidate |

Neither product maps electrical conductivity or salt-affected status, so neither enters as a
salinity observation. They are covariates, and their own uncertainty is large enough that they
cannot drive a class boundary. The texture layers matter twice over: they set the 1:5 to ECe
conversion interval per texture class.

## Field truth for salinity

There is no open, georeferenced topsoil EC dataset for Casamance that this project has located, and
no partner data yet. The measurement basis that matters is the 1:5 extract, because that is what
Casamance laboratories report: published values from the Bignona and Mlomp studies run
0.01–9.77 mS/cm on that basis. Conversion to ECe is a fitted, texture-dependent offset, never one
global factor, and with no paired samples it enters as a literature interval per texture class.

Known published field campaigns, useful as leads rather than as data:

| Study | Field data | Date of field work | Access |
|-------|-----------|--------------------|--------|
| Djilor district, Fatick (Saloum, not Casamance) | 300 topsoil samples, 0–30 cm, EC | 2017 imagery; sampling year not stated in abstract | paper open access, point coordinates not published |
| Northern Saloum estuary (Tine, Faye, Diedhiou) | ground-truth points for class validation | accepted 2026-04-01, published 2026 | paper open access, coordinates on request |
| Boutolate sub-watershed, Basse-Casamance | soil samples and floristic plots, 3 × 3 m | Landsat 1984–2010 study, published 2014 | paper open access, coordinates not published |
| Diouloulou watershed, northern Basse-Casamance | soil physicochemical analysis, water salinity, household surveys | thesis 2023 | thesis open access, point data not published |
| Casamance estuary salinity | point measurements | 2023-12 | conference paper 2024 |

The partner request goes to UASZ, ISRA and SODAGRI. Enrolment minimum per record: coordinates with
positional uncertainty, sampling date, depth and depth convention, EC method (1:5 extract or
saturated paste, stated) with the ratio where 1:5, pH, laboratory, and licence terms.

## Administrative and socio-economic context

| Source | Date represented | Use | Licence | Status |
|--------|------------------|-----|---------|--------|
| geoBoundaries SEN ADM2 | verify on fetch | working extent and commune-level aggregation | CC BY 3.0 IGO | phase 0 |
| ANAT / GeoSenegal layers | verify on fetch | dike and hydro-agricultural infrastructure, if licensable | check per layer | unverified |

Dike locations are the one context layer that could materially change the story (protected versus
unprotected lowland). No confirmed open georeferenced source yet; treat as open decision in
`docs/PLAN.md` §9.

## Rules

- Every file written into `data/raw/` gets a registry row: URL, retrieval date, licence, SHA-256.
- Data contents are git-ignored; folders and their READMEs are tracked.
- No dataset is described without its date. A product with an epoch gets the epoch; an acquisition
  gets the window; a download gets the retrieval date.
- No layer is described without its measurement basis. ECe is never shown without the 1:5 basis
  that produced it.
