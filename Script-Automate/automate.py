import json
import random
import os
from datetime import datetime, timedelta

# --- Directories ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # directory of automate.py
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)

ACTIVITIES_FILE = os.path.join(DATA_DIR, "activities.json")
JSONL_FILE = os.path.join(DATA_DIR, "youthletics_contacts.jsonl")

# --- Load dynamic activities ---
with open(ACTIVITIES_FILE, "r", encoding="utf-8") as f:
    activities_data = json.load(f)

def flatten_activities(category_dict):
    all_items = []
    for items in category_dict.values():
        all_items.extend(items)
    return all_items

sports_activities = flatten_activities(activities_data["sports"])
arts_activities = flatten_activities(activities_data["arts"])
music_activities = flatten_activities(activities_data["music"])

# --- German Names ---
first_names = [
    "Anna", "Lena", "Julia", "Laura", "Sophie", "Maria", "Clara", "Emilia",
    "Max", "Paul", "Leon", "Jonas", "Noah", "Elias", "Felix", "Moritz"
]
last_names = [
    "Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Wagner",
    "Becker", "Hoffmann", "Schäfer", "Koch", "Bauer", "Richter", "Klein", "Wolf"
]
email_providers = ["gmail.com", "gmx.de", "web.de", "t-online.de", "outlook.de"]

# --- Köln Stadtteile ---
koeln_stadtteile = [
    "Altstadt-Nord", "Altstadt-Süd", "Deutz", "Ehrenfeld", "Nippes", "Mülheim",
    "Chorweiler", "Porz", "Rodenkirchen", "Lindenthal", "Kalk", "Dellbrück",
    "Humboldt/Gremberg", "Vingst", "Bickendorf", "Weidenpesch", "Niehl",
    "Riehl", "Holweide", "Brück", "Wahnheide", "Zollstock", "Bayenthal",
    "Raderberg", "Sülz", "Braunsfeld", "Vogelsang", "Esch/Auweiler"
]

def generate_email(first, last):
    num = random.randint(1, 999)
    return f"{first.lower()}.{last.lower()}{num}@{random.choice(email_providers)}"

def random_timestamp(days_back=180):
    now = datetime.now()
    random_days = random.randint(0, days_back)
    random_time = timedelta(
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )
    random_date = now - timedelta(days=random_days)
    return (random_date.replace(hour=0, minute=0, second=0, microsecond=0) + random_time).strftime("%Y-%m-%d %H:%M:%S")

def generate_entry():
    first = random.choice(first_names)
    last = random.choice(last_names)
    name = f"{first} {last}"
    email = generate_email(first, last)
    child_age = random.randint(1, 17)

    selected_sports = random.sample(sports_activities, random.randint(0, 3))
    selected_arts = random.sample(arts_activities, random.randint(0, 2))
    selected_music = random.sample(music_activities, random.randint(0, 2))
    if not (selected_sports or selected_arts or selected_music):
        selected_sports = random.sample(sports_activities, 1)

    stadtteil = random.choice(koeln_stadtteile)
    location = {
        "ip": f"80.123.{random.randint(0,255)}.{random.randint(0,255)}",
        "city": "Köln",
        "region": "Nordrhein-Westfalen",
        "country": "DE",
        "stadtteil": stadtteil,
        "coordinates": "50.9375,6.9603"
    }

    timestamp = random_timestamp()

    return {
        "timestamp": timestamp,
        "name": name,
        "email": email,
        "child_age": child_age,
        "activities": {
            "sports": selected_sports,
            "arts": selected_arts,
            "music": selected_music
        },
        "location": location
    }

def save_to_jsonl(entry, filename=JSONL_FILE):
    with open(filename, mode="a", encoding="utf-8") as f:
        json.dump(entry, f, ensure_ascii=False)
        f.write("\n")

if __name__ == "__main__":
    num_entries = 15000
    for _ in range(num_entries):
        entry = generate_entry()
        save_to_jsonl(entry)
    print(f"✅ Generated {num_entries} mock entries in {JSONL_FILE}")
