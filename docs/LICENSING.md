# Licensing

Two licences, split by what is being licensed.

**Code** — Apache-2.0, full text in `LICENSE`. Covers `app/`, `scripts/`, notebooks, and any other
executable or configuration file. Permits commercial use, modification and redistribution, with a
patent grant and attribution requirements.

**Data, documentation and map products** — CC BY 4.0. Covers everything under `data/aoi/`,
`data/derived/` (our own products), `docs/`, and the text of this repository. Attribution:
"Soberana Sensing, Soberana Salinization Monitor", with the version or retrieval date.

Third-party data keeps its own licence and is never relicensed by us. Per-source licences are in
`docs/DATA.md`; the mandatory attributions are:

- Sentinel-1 and Sentinel-2: Copernicus data, free and open under the Copernicus Data Space
  Ecosystem terms.
- Landsat: USGS, public domain.
- Copernicus DEM: © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018, provided
  under COPERNICUS by ESA and the EU. Used as the basis of DeltaDTM; keep the notice if any GLO-30
  layer ships.
- DeltaDTM v1.1: Deltares and TU Delft, CC BY 4.0, doi 10.4121/21997565.
- ERA5-Land: Copernicus Climate Change Service, licence per the CDS terms of use.
- GSASmap v1.0: FAO Global Soil Partnership, cite the 2024 report; the national raster is supplied
  under the terms agreed in the data request and is not redistributed beyond those terms.
- HWSD v2: FAO and ISRIC, licence to be confirmed on fetch.
- CHIRPS: Climate Hazards Center, UC Santa Barbara, public domain (CC0).
- JRC Global Surface Water: © European Union, Copernicus.
- Global Mangrove Watch: CC BY 4.0.
- geoBoundaries: CC BY 3.0 IGO.
- iSDAsoil and SoilGrids: CC BY 4.0 (ISRIC / iSDA).

Before publishing a derived map, re-check every input licence. A product that mixes sources
inherits the strictest attribution requirement among them.
