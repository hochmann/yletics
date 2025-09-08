import streamlit as st
import pandas as pd
import os
from collections import Counter, defaultdict
import folium
from streamlit_folium import st_folium
import json

JSONL_FILE = "youthletics_contacts.jsonl"
GEOJSON_FILE = "geo_info/koeln_stadtteile.geojson"

# Load JSONL
def load_data():
    if os.path.exists(JSONL_FILE):
        return pd.read_json(JSONL_FILE, lines=True)
    else:
        return pd.DataFrame()

st.title("📊 Youth-Letics - Overview Dashboard")

df = load_data()

if df.empty:
    st.info("No entries yet.")
else:
    # --- Compute Stadtteil stats ---
    def extract_stadtteile(df):
        stadtteile = []
        for loc in df["location"].dropna():
            if isinstance(loc, dict) and "stadtteil" in loc:
                stadtteile.append(loc["stadtteil"])
        return stadtteile

    all_stadtteile = extract_stadtteile(df)
    stadtteil_stats = defaultdict(lambda: {"total": 0, "sports": 0, "arts": 0, "music": 0})
    for _, row in df.iterrows():
        stadt = row["location"].get("stadtteil") if isinstance(row["location"], dict) else None
        if stadt:
            stadtteil_stats[stadt]["total"] += 1
            if any(row["activities"].get("sports", [])):
                stadtteil_stats[stadt]["sports"] += 1
            if any(row["activities"].get("arts", [])):
                stadtteil_stats[stadt]["arts"] += 1
            if any(row["activities"].get("music", [])):
                stadtteil_stats[stadt]["music"] += 1

    stadtteil_df = pd.DataFrame(
        [(k, v["total"], v["sports"], v["arts"], v["music"]) for k, v in stadtteil_stats.items()],
        columns=["Stadtteil", "Total", "Sports", "Arts", "Music"]
    ).sort_values(by="Total", ascending=False)

    # --- Choropleth Map ---
    st.subheader("🗺️ Cologne Choropleth Map of Entries")

    if os.path.exists(GEOJSON_FILE):
        # --- Normalize helper ---
        def normalize_name(name: str):
            return name.strip().replace("ß", "ss")

        # Normalize names in data
        df["location"] = df["location"].apply(
            lambda loc: {**loc, "stadtteil": normalize_name(loc["stadtteil"])} if isinstance(loc, dict) and "stadtteil" in loc else loc
        )

        # Load & normalize GeoJSON
        with open(GEOJSON_FILE, "r", encoding="utf-8") as f:
            geojson_data = json.load(f)
        for feature in geojson_data["features"]:
            feature["properties"]["name"] = normalize_name(feature["properties"]["name"])

        # Merge all GeoJSON names into DF (0 for missing)
        all_geo_names = [f["properties"]["name"] for f in geojson_data["features"]]
        stadtteil_df = stadtteil_df.set_index("Stadtteil").reindex(all_geo_names, fill_value=0).reset_index().rename(columns={"index": "Stadtteil"})

        # Inject stats into geojson
        for feature in geojson_data["features"]:
            name = feature["properties"]["name"]
            stats = stadtteil_stats.get(name, {"total": 0, "sports": 0, "arts": 0, "music": 0})
            feature["properties"].update({
                "total": stats["total"],
                "sports": stats["sports"],
                "arts": stats["arts"],
                "music": stats["music"]
            })

        # Normalize coloring by total entries
        max_count = stadtteil_df["Total"].max()
        stadtteil_df["Normalized"] = stadtteil_df["Total"] / max_count if max_count > 0 else 0

        # Build map
        city_map = folium.Map(location=[50.9375, 6.9603], zoom_start=11, tiles="cartodb positron")
        folium.Choropleth(
            geo_data=geojson_data,
            data=stadtteil_df,
            columns=["Stadtteil", "Normalized"],
            key_on="feature.properties.name",
            fill_color="YlOrRd",
            fill_opacity=0.8,
            line_opacity=0.3,
            legend_name="Relative Entry Density"
        ).add_to(city_map)

        # Tooltips
        folium.GeoJson(
            geojson_data,
            name="Stadtteile",
            tooltip=folium.GeoJsonTooltip(
                fields=["name", "total", "sports", "arts", "music"],
                aliases=["Stadtteil:", "Total Entries:", "Sports:", "Arts:", "Music:"],
                localize=True
            ),
        ).add_to(city_map)

        st_folium(city_map, width=700, height=500)
    else:
        st.info("GeoJSON file for Köln Stadtteile not found. Choropleth map cannot be displayed.")
