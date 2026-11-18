"""Casamance salinization dashboard.

Scaffold: renders the AOI and the data inventory. Product layers land under data/derived/.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pydeck as pdk
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
AOI_DIR = ROOT / "data" / "aoi"
DERIVED = ROOT / "data" / "derived"

SALINITY_CLASSES = pd.DataFrame(
    [
        (0, "0-2", "non-saline"),
        (1, "2-4", "slightly saline"),
        (2, "4-8", "moderately saline"),
        (3, "8-16", "strongly saline"),
        (4, ">16", "extremely saline"),
    ],
    columns=["class", "EC dS/m", "label"],
)

SEASONS = {"dry (Nov-May)": (11, 5), "wet (Jun-Oct)": (6, 10)}


@st.cache_data
def load_aoi(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def bounds(geojson: dict) -> list[float]:
    xs: list[float] = []
    ys: list[float] = []

    def walk(node):
        if isinstance(node[0], (int, float)):
            xs.append(node[0])
            ys.append(node[1])
        else:
            for part in node:
                walk(part)

    for feature in geojson["features"]:
        walk(feature["geometry"]["coordinates"])
    return [min(xs), min(ys), max(xs), max(ys)]


def aoi_options() -> dict[str, Path]:
    if not AOI_DIR.exists():
        return {}
    return {p.stem.replace("-", " ").title(): p for p in sorted(AOI_DIR.glob("*.geojson"))}


def render_map(geojson: dict, view_state: pdk.ViewState) -> None:
    layer = pdk.Layer(
        "GeoJsonLayer",
        geojson,
        opacity=0.25,
        stroked=True,
        filled=True,
        get_fill_color=[214, 96, 77, 90],
        get_line_color=[120, 40, 30, 220],
        get_line_width=2,
        line_width_min_pixels=1,
        pickable=True,
    )
    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "{name}"},
            map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        )
    )


def derived_inventory() -> pd.DataFrame:
    files = sorted(DERIVED.glob("**/*")) if DERIVED.exists() else []
    rows = [
        (f.relative_to(ROOT).as_posix(), f"{f.stat().st_size / 1e6:.1f} MB")
        for f in files
        if f.is_file() and f.name != "README.md"
    ]
    return pd.DataFrame(rows, columns=["path", "size"])


def main() -> None:
    st.set_page_config(page_title="Soberana Salinization Monitor", layout="wide")
    st.title("Soberana Salinization Monitor")
    st.caption(
        "Soil salinization mapping and monitoring, Casamance, Senegal. "
        "Scaffold, 2026-11-18: boundaries only, no map product yet."
    )

    options = aoi_options()
    if not options:
        st.error("No AOI found under data/aoi/. Run scripts/fetch_aoi.py first.")
        return

    with st.sidebar:
        st.header("View")
        name = st.selectbox("Area of interest", list(options))
        season = st.selectbox("Season", list(SEASONS))
        years = st.slider("Epoch window", 1984, 2026, (2016, 2026))
        st.divider()
        st.subheader("Layers")
        st.checkbox("Salinity class", value=True, disabled=True, help="No product yet")
        st.checkbox("Acid sulfate flag", value=False, disabled=True, help="No product yet")
        st.checkbox("Mangrove history", value=False, disabled=True, help="No product yet")
        st.checkbox("Surface water", value=False, disabled=True, help="No product yet")
        st.caption("Layers unlock as products land in data/derived/.")

    geojson = load_aoi(str(options[name]))
    west, south, east, north = bounds(geojson)
    view = pdk.ViewState(
        latitude=(south + north) / 2,
        longitude=(west + east) / 2,
        zoom=8.6 if (east - west) < 1.5 else 7.8,
        pitch=0,
    )

    tab_map, tab_method, tab_data = st.tabs(["Map", "Method", "Data"])

    with tab_map:
        left, right = st.columns([3, 1])
        with left:
            render_map(geojson, view)
        with right:
            st.metric("Regions in view", len(geojson["features"]))
            st.metric("Season", season)
            st.metric("Epoch window", f"{years[0]}-{years[1]}")
            st.write("Bounds, EPSG:4326")
            st.code(f"{west:.3f}, {south:.3f}\n{east:.3f}, {north:.3f}")
        st.subheader("Planned salinity classes")
        st.dataframe(SALINITY_CLASSES, hide_index=True, use_container_width=True)
        st.caption(
            "EC of the saturated paste extract, topsoil 0-30 cm, dS/m at 25 C. "
            "USDA/NRCS breakpoints, the same ones used in the Senegalese salinity literature."
        )

    with tab_method:
        st.markdown(
            """
**What this will map.** Salinity class per lowland polygon, with an acid sulfate flag kept on a
separate axis. Sentinel-2 L2A surface reflectance supplies the spectral signal, Sentinel-1 C-band
adds surface roughness and moisture, Copernicus DEM supplies elevation and distance-to-water terms.

**What it cannot promise.** Optical indices confuse surface salt with dry mudflat and dead
mangrove. The map is a validated classification or it is not published. Published Senegalese
work reaches R² 0.73 for EC in the Saloum (Djilor, 300 topsoil samples, Landsat 2017) and
0.94-0.98 overall accuracy with Sentinel-2 plus Sentinel-1; neither transfers to Casamance
without local field labels.

**Change detection.** Same-season epochs, direct class comparison, transition matrix, rainfall
anomaly shown beside the change map. Cross-sensor comparisons are labelled lower confidence.

Full plan: `docs/PLAN.md`.
            """
        )

    with tab_data:
        st.subheader("AOI source")
        props = geojson["features"][0]["properties"]
        st.json(props)
        st.subheader("Products in data/derived/")
        inventory = derived_inventory()
        if inventory.empty:
            st.info("No derived product yet.")
        else:
            st.dataframe(inventory, hide_index=True, use_container_width=True)
        st.subheader("Source inventory")
        st.code("docs/DATA.md", language=None)
        st.caption(f"Epoch window selected: {years[0]}-{years[1]}; season: {season}.")


if __name__ == "__main__":
    main()
