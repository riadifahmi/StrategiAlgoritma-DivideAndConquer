# fetch_places.py
# Ambil data tempat dari Google Places API (textsearch) dan simpan ke data/raw_data.json
# Usage: python fetch_places.py

import requests
import time
import json
import urllib.parse

API_KEY = "YOUR_API_KEY"   # ganti dengan API key-mu
OUTPUT_FILE = "data/raw_data.json"

# Contoh query list (kamu bisa tambahkan variasi kata kunci)
QUERIES = [
    "wisata Malang",
    "tempat wisata Batu",
    "cafe Malang",
    "pelesiran Malang",
    "tourist attractions Malang"
]

def fetch_textsearch(query, api_key, page_token=None):
    base = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": query,
        "key": api_key,
        "language": "id"
    }
    if page_token:
        params["pagetoken"] = page_token
    url = base + "?" + urllib.parse.urlencode(params)
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def fetch_all_for_query(query, api_key, pause=2.5):
    results = []
    r = fetch_textsearch(query, api_key)
    results.extend(r.get("results", []))
    next_token = r.get("next_page_token")
    # next_page_token butuh jeda beberapa detik sebelum bisa dipakai
    while next_token:
        time.sleep(pause)
        r = fetch_textsearch(query, api_key, page_token=next_token)
        results.extend(r.get("results", []))
        next_token = r.get("next_page_token")
    return results

def normalize_place(place):
    # ambil field utama, safe-get karena tidak semua tempat punya semua field
    return {
        "place_id": place.get("place_id"),
        "name": place.get("name"),
        "address": place.get("formatted_address") or place.get("vicinity"),
        "lat": place.get("geometry", {}).get("location", {}).get("lat"),
        "lng": place.get("geometry", {}).get("location", {}).get("lng"),
        "rating": place.get("rating"),
        "user_ratings_total": place.get("user_ratings_total"),
        "types": place.get("types", []),
        # placeholder: detail reviews perlu panggil Place Details API jika dibutuhkan
        "has_details": False
    }

def main():
    all_places = {}
    for q in QUERIES:
        try:
            print(f"Fetching query: {q}")
            places = fetch_all_for_query(q, API_KEY)
            for p in places:
                pid = p.get("place_id")
                if pid and pid not in all_places:
                    all_places[pid] = normalize_place(p)
            time.sleep(1)
        except Exception as e:
            print("Error:", e)
    # save
    data = list(all_places.values())
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(data)} places to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

