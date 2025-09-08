import streamlit as st
import json
import os
from datetime import datetime
import requests

JSONL_FILE = "youthletics_contacts.jsonl"

# Save entry to JSONL file
def save_to_jsonl(entry, filename=JSONL_FILE):
    with open(filename, mode="a", encoding="utf-8") as f:
        json.dump(entry, f)
        f.write("\n")

# Get IP-based location
def get_location():
    try:
        response = requests.get("https://ipinfo.io")
        data = response.json()
        return {
            "ip": data.get("ip", ""),
            "city": data.get("city", ""),
            "region": data.get("region", ""),
            "country": data.get("country", ""),
            "loc": data.get("loc", "")
        }
    except Exception:
        return {
            "ip": "", "city": "", "region": "", "country": "", "loc": ""
        }

# Activity Options
sports_activities = [
    "Baby Swimming", "Baby Yoga", "Toddler Gymnastics", "Kids Gymnastics",
    "Dance (Ballet, Hip-Hop, Contemporary)", "Soccer / Football", "Basketball",
    "Tennis", "Martial Arts (Karate, Judo, Taekwondo)", "Climbing / Bouldering",
    "Track & Field / Athletics", "Cycling / BMX", "Swimming", "Skateboarding / Roller Sports"
]
arts_activities = [
    "Baby Sensory Play", "Drawing & Painting", "Crafts & DIY", "Sculpture / Clay Art",
    "Digital Art", "Theater & Drama", "Dance (Creative Movement)", "Storytelling & Creative Writing"
]
music_activities = [
    "Baby Music Classes (Rhythm & Sound Play)", "Singing & Choir", "Piano", "Guitar",
    "Violin", "Drums / Percussion", "Music Production (Teens)"
]

# UI
st.title("🏃‍♂️ Youth-Letics - Sport & Fun for Kids")
st.subheader("Join the movement to empower kids through sports, arts & music!")

st.markdown("Please leave your details and select activities of interest. We’ll get in touch soon!")

with st.form("contact_form", clear_on_submit=True):
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")
    child_age = st.number_input("Child's Age", min_value=1, max_value=17, step=1)

    st.markdown("### Select Activities of Interest")
    selected_sports = st.multiselect("Sports Activities", options=sports_activities)
    selected_arts = st.multiselect("Arts & Creativity Activities", options=arts_activities)
    selected_music = st.multiselect("Music Activities", options=music_activities)

    # Sidebar summary of selections
    with st.sidebar:
        st.header("Your Selected Activities")
        if selected_sports or selected_arts or selected_music:
            if selected_sports:
                st.markdown("**Sports:**")
                st.write(", ".join(selected_sports))
            if selected_arts:
                st.markdown("**Arts & Creativity:**")
                st.write(", ".join(selected_arts))
            if selected_music:
                st.markdown("**Music:**")
                st.write(", ".join(selected_music))
        else:
            st.info("No activities selected yet.")

    submit = st.form_submit_button("Submit")

    if submit:
        if name and email and (selected_sports or selected_arts or selected_music):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            location = get_location()
            entry = {
                "timestamp": timestamp,
                "name": name,
                "email": email,
                "child_age": child_age,
                "activities": {
                    "sports": selected_sports,
                    "arts": selected_arts,
                    "music": selected_music
                },
                "location": {
                    "ip": location["ip"],
                    "city": location["city"],
                    "region": location["region"],
                    "country": location["country"],
                    "coordinates": location["loc"]
                }
            }
            save_to_jsonl(entry)
            st.success(f"Thanks {name}, your info has been saved!")
        else:
            st.warning("Please fill in your name, email, and select at least one activity.")
