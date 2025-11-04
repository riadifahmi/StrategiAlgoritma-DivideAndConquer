# =============================================
# File: preprocessing.py
# Fungsi: Membersihkan data wisata hasil scraping
# =============================================

import json
import pandas as pd
from geopy.distance import geodesic
import re
import os

RAW_FILE = "data/raw_data.json"
CLEAN_FILE = "data/clean_data.json"

CENTER_MALANG = (-7.9666, 112.6326)

def clean_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\-']", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def compute_distance(lat, lng):
    try:
        return round(geodesic(CENTER_MALANG, (lat, lng)).km, 2)
    except:
        return None

def main():
    os.makedirs("data", exist_ok=True)
    with open(RAW_FILE, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    cleaned_data = []
    for item in raw_data:
        if not item.get("name"):
            continue

        cleaned_data.append({
            "name": item.get("name"),
            "name_clean": clean_text(item.get("name")),
            "address": item.get("address"),
            "lat": item.get("lat"),
            "lng": item.get("lng"),
            "rating": item.get("rating", 0),
            "user_ratings_total": item.get("user_ratings_total", 0),
            "reviews_text": clean_text(item.get("reviews_text")),
            "types": ",".join(item.get("types", [])),
            "distance_km": compute_distance(item.get("lat"), item.get("lng"))
        })

    with open(CLEAN_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Data bersih disimpan ({len(cleaned_data)} tempat) → {CLEAN_FILE}")

if __name__ == "__main__":
    main()
