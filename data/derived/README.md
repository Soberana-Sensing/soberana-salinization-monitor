# data/derived

Analysis outputs the dashboard reads. Class maps, change layers, polygons, accuracy tables.

Suggested naming: `salinity_<aoi>_<season>-<year>_v<n>.tif`, `change_<aoi>_<y1>_<y2>_v<n>.tif`,
`validation_<aoi>_<date>.csv`. Keep the version; a map revision is a new file, never an overwrite.

Not tracked. Every product carries its epoch, its training-label date range, and its validation
score in `docs/` before it reaches the dashboard.
