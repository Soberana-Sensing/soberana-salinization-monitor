# data

Data layout for the salinization monitor. Contents are git-ignored except the AOI boundaries and
these README files; folders stay tracked so the layout is self-documenting.

| Folder | Content | Tracked |
|--------|---------|---------|
| `aoi/` | area-of-interest boundaries | yes |
| `raw/` | data as delivered, one folder per source | README + registry only |
| `interim/` | reshaped intermediates, composites, stacks | README only |
| `derived/` | analysis outputs the dashboard reads | README only |

Every dataset reference carries its date: acquisition window, product epoch, or retrieval date. No
bare data.

Sources, licences and dates: `docs/DATA.md`.
