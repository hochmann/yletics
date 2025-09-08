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

    # --- Chart: Submissions Per Day ---
    st.subheader("📅 Submissions Per Day")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = df["timestamp"].dt.date
    stats = df.groupby("date").size().reset_index(name="entries")
    if not stats.empty:
        st.bar_chart(data=stats, x="date", y="entries")
    else:
        st.info("No submissions available.")

    # --- Flatten activities for popularity ---
    def extract_activities(df, category):
        activities = []
        for acts in df["activities"].dropna():
            if isinstance(acts, dict) and category in acts:
                activities.extend(acts[category])
        return activities

    st.subheader("Most Popular Activities")
    category_map = {"Sports": "sports", "Arts": "arts", "Music": "music"}
    category = st.selectbox("Select category to view popularity:", list(category_map.keys()))
    selected_cat = category_map[category]
    all_activities = extract_activities(df, selected_cat)

    if all_activities:
        counts = Counter(all_activities)
        activities_df = pd.DataFrame(counts.items(), columns=["Activity", "Count"]).sort_values(by="Count", ascending=False)
        st.bar_chart(activities_df.set_index("Activity"))
    else:
        st.info("No data for this category yet.")
