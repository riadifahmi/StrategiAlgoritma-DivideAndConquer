# =============================================
# File: fetch_places.py
# Fungsi: Mengambil data wisata + ulasan pengguna dari Google Maps API
# =============================================

import requests
import time
import json
import urllib.parse
import os

# ⚠️ Ganti dengan API key kamu
API_KEY = "AIzaSyDzCGGN9TuYUZREiKncaR2xsJpHIsgajoww"

# Folder output data
os.makedirs("data", exist_ok=True)
OUTPUT_FILE = "data/raw_data.json"

# Kata kunci pencarian
QUERIES = [
    "wisata Malang",
    "tempat wisata Batu",
    "cafe Malang",
    "pantai malang",
    "gunung malang",
    "air terjun malang"
]

# === Fungsi ambil data utama ===
def fetch_textsearch(query, api_key, page_token=None):
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": query,
        "key": api_key,
        "language": "id"
    }
    if page_token:
        params["pagetoken"] = page_token

    url = base_url + "?" + urllib.parse.urlencode(params)
    response = requests.get(url)
    return response.json()

# === Fungsi ambil review tambahan ===
def fetch_reviews(place_id):
    base_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "review",
        "language": "id",
        "key": API_KEY
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    reviews = data.get("result", {}).get("reviews", [])
    texts = [r.get("text", "") for r in reviews if r.get("text")]
    return " ".join(texts[:3]) if texts else ""

# === Proses utama ===
def fetch_all_places():
    all_places = {}
    for q in QUERIES:
        print(f"🔍 Mengambil data: {q}")
        result = fetch_textsearch(q, API_KEY)
        results = result.get("results", [])
        next_page = result.get("next_page_token")

        for place in results:
            pid = place.get("place_id")
            if not pid:
                continue

            reviews_text = fetch_reviews(pid)
            time.sleep(1)  # jeda antar request

            all_places[pid] = {
                "name": place.get("name"),
                "address": place.get("formatted_address"),
                "lat": place.get("geometry", {}).get("location", {}).get("lat"),
                "lng": place.get("geometry", {}).get("location", {}).get("lng"),
                "rating": place.get("rating"),
                "user_ratings_total": place.get("user_ratings_total"),
                "reviews_text": reviews_text,
                "types": place.get("types", [])
            }

        # Halaman berikut (pagination)
        while next_page:
            print("➡️ Mengambil halaman selanjutnya...")
            time.sleep(3)
            result = fetch_textsearch(q, API_KEY, page_token=next_page)
            results = result.get("results", [])
            next_page = result.get("next_page_token")

            for place in results:
                pid = place.get("place_id")
                if not pid:
                    continue

                reviews_text = fetch_reviews(pid)
                time.sleep(1)

                all_places[pid] = {
                    "name": place.get("name"),
                    "address": place.get("formatted_address"),
                    "lat": place.get("geometry", {}).get("location", {}).get("lat"),
                    "lng": place.get("geometry", {}).get("location", {}).get("lng"),
                    "rating": place.get("rating"),
                    "user_ratings_total": place.get("user_ratings_total"),
                    "reviews_text": reviews_text,
                    "types": place.get("types", [])
                }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(list(all_places.values()), f, ensure_ascii=False, indent=2)

    print(f"\n✅ Berhasil menyimpan {len(all_places)} data ke {OUTPUT_FILE}")

if __name__ == "__main__":
    fetch_all_places()
