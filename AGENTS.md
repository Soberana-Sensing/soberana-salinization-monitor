# AGENTS.md — Soberana Salinization Monitor

Rules for AI agents in this repo. Loaded every session that opens this directory.

## What this project is

Map and monitor soil salinization from free satellite data and serve it as a dashboard. Delivered
quantity: ECe in dS/m at 0–30 cm and 30–100 cm, with the 1:5 extract basis declared beside it.
Working extent: Lower Casamance, the geoBoundaries SEN ADM2 union of Bignona, Oussouye and
Ziguinchor departments. Scaffold created 2026-11-18. The binding plan is `docs/PLAN.md`; it
overrides any preference stated elsewhere once approved.

## Order of attack

1. `~/.config/opencode/soberana-salinization-monitor_MEMORY.md` (create on first durable fact)
2. `~/.config/opencode/pools/soberana-salinization-monitor/` when it exists
3. `docs/PLAN.md`, then `docs/DATA.md`
4. Papers as extracted text only: `~/.config/opencode/tools/pdftext.py`. Never upload a PDF.

## Data

`data/raw/`, `data/interim/`, `data/derived/`. Contents git-ignored, folders tracked.
`data/aoi/` is tracked because it holds small, citable boundaries.

Every dataset reference carries its date: acquisition window, product epoch, or retrieval date. No
bare data. Register every fetch with URL, retrieval date, licence and SHA-256 in `data/raw/REGISTRY.csv`.

Never run a fetch that writes into `data/` without being asked.

Check for `soberana-salinization-monitor-venv/` before running Python. Never install into system
Python.

## Science

- SoilGrids and iSDAsoil carry no electrical conductivity. They are covariates, never salinity
  observations.
- GSASmap is the only ECe prior with a national figure for Senegal, and its raster is not open. Until
  it is released, the static product is a covariate-only risk index and is labelled that way.
- The GSASmap Senegal subsoil figure (12.4 km² at 30–100 cm) is a broken submission, not low
  salinity at depth. Do not use subsoil GSASmap for Senegal.
- Salinity class thresholds follow the USDA/NRCS ECe breakpoints in `docs/PLAN.md` §3. Keep acid
  sulfate status as a separate axis.
- Casamance laboratories report 1:5 extract, not saturated paste. The 1:5 to ECe conversion is a
  fitted texture-dependent offset; with no paired samples it is a literature interval per texture
  class, flagged. Never apply one global conversion factor.
- A class map without a validation-based uncertainty statement is not a product.
- Any hectare figure comes from an equal-area projection, never EPSG:3857.

## Git

Public repo under the `Soberana-Sensing` org. No push, force-push, branch delete, or destructive git
without asking first. Commit messages: Conventional Commits, terse intent.

## Gates before publishing a map

1. Labels used for validation are dated, georeferenced, and outside the training set.
2. Confusion matrix reported per class, including the mudflat/salt-crust error.
3. Rainfall anomaly of the change period shown beside the change map.
4. Uncertainty layer present, and the method page states what the map cannot tell.
5. The 1:5 basis is declared beside every ECe figure, with the conversion interval stated.
6. No "monitoring" verb and no trend claim on any layer while local ECe dated before 2021 is the
   only evidence. The static product ships as a prior-conditioned risk indicator.
