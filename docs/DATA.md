# Data inventory

Every source carries its date, its resolution, its licence and its status. Retrieval dates are for
the scaffold session, 2026-11-18, unless stated otherwise. Nothing here is downloaded yet beyond
the area boundaries.

## Boundaries

| Source | Date represented | Access | Licence | Status |
|--------|------------------|--------|---------|--------|
| geoBoundaries gbOpen SEN ADM1 | boundaryYearRepresented 2019, build 2023-12-12, source update 2023-01-19 | `data/aoi/`, fetched 2026-11-18 via `scripts/fetch_aoi.py` | CC BY 3.0 IGO | in repo |

Senior administrative units used: Ziguinchor (phase 1), plus Sédhiou and Kolda for the wider
Casamance. Boundary positions are simplified geometries; for anything at parcel scale, replace
with a surveyed or national boundary source.

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
| Copernicus DEM GLO-30 | acquisitions 2011-01 to 2015-12, release 2021 | 30 m | Copernicus, free with attribution | planned |
| JRC Global Surface Water v1.4 | 1984-01 to 2021-12 | 30 m | Copernicus/JRC, free with attribution | planned |
| Global Mangrove Watch v3.0 | 1996 to 2020, 11 epochs | 25 m | CC BY 4.0 | planned |
| CHIRPS v2.0 daily rainfall | 1981-01 onward | 0.05° (~5.5 km) | public domain, CC0 | planned |

## Soil context, with the reason each is not a salinity prior

| Source | Date represented | Why it is here | Licence | Status |
|--------|------------------|----------------|---------|--------|
| iSDAsoil Africa 30 m | epoch 2001-01-01 to 2017-01-01, covariates Sentinel-2 2018–2019 percentiles | texture, pH, drainage context; no EC, no salt content | CC BY 4.0 | candidate |
| SoilGrids 2.0 250 m | WoSIS snapshot 2020-01, covariate windows 2001–2015 | texture, bulk density, drainage context; no EC | CC BY 4.0 | candidate |

Neither product maps electrical conductivity or salt-affected status, so neither can be ingested as
a salinity observation. They are covariates at best, and their own uncertainty is large enough that
they cannot drive a class boundary.

## Field truth for salinity

There is no open, georeferenced topsoil EC dataset for Casamance that this project has located.
The candidate routes are recorded in `docs/PLAN.md` §5.5. Known published field campaigns, useful
as leads rather than as data:

| Study | Field data | Date of field work | Access |
|-------|-----------|--------------------|--------|
| Djilor district, Fatick (Saloum, not Casamance) | 300 topsoil samples, 0–30 cm, EC | 2017 imagery; sampling year not stated in abstract | paper open access, point coordinates not published |
| Northern Saloum estuary (Tine, Faye, Diedhiou) | ground-truth points for class validation | accepted 2026-04-01, published 2026 | paper open access, coordinates on request |
| Boutolate sub-watershed, Basse-Casamance | soil samples and floristic plots, 3 × 3 m | Landsat 1984–2010 study, published 2014 | paper open access, coordinates not published |
| Diouloulou watershed, northern Basse-Casamance | soil physicochemical analysis, water salinity, household surveys | thesis 2023 | thesis open access, point data not published |
| Casamance estuary salinity | point measurements | 2023-12 | conference paper 2024 |

If a partner supplies data, the enrolment minimum per record is: coordinates with positional
uncertainty, sampling date, depth and depth convention, EC method (1:5 extract or saturated paste,
stated), pH, laboratory, and licence terms.

## Administrative and socio-economic context

| Source | Date represented | Use | Licence | Status |
|--------|------------------|-----|---------|--------|
| geoBoundaries SEN ADM2 | verify on fetch | commune-level aggregation | CC BY 3.0 IGO | planned |
| ANAT / GeoSenegal layers | verify on fetch | dike and hydro-agricultural infrastructure, if licensable | check per layer | unverified |

Dike locations are the one context layer that could materially change the story (protected versus
unprotected lowland). No confirmed open georeferenced source yet; treat as open decision in
`docs/PLAN.md` §9.

## Rules

- Every file written into `data/raw/` gets a registry row: URL, retrieval date, licence, SHA-256.
- Data contents are git-ignored; folders and their READMEs are tracked.
- No dataset is described without its date. A product with an epoch gets the epoch; an acquisition
  gets the window; a download gets the retrieval date.
