# src/main.py
import argparse
import pandas as pd
from recommender import divide_and_conquer
from utils import clean_text
import os
import geocoder

DEFAULT_EXCEL = "/mnt/data/Scraping_Clustering_Wisata_Malang.xlsx"

def load_data(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    # baca excel, menyesuaikan kolom yang ada pada dataset Anda
    df = pd.read_excel(path, engine="openpyxl")
    # kolom yang diharapkan minimal: name, lat, lng, rating, reviews_text, address/time (bila ada)
    # normalize column names
    df.columns = [c.strip() for c in df.columns]
    return df

def df_to_items(df):
    items = []
    for _, row in df.iterrows():
        items.append({
            "name": row.get("name") or row.get("Name") or row.get("nama") or "",
            "lat": row.get("lat") or row.get("latitude") or row.get("Lat") or None,
            "lng": row.get("lng") or row.get("longitude") or row.get("Lng") or None,
            "rating": row.get("rating") if "rating" in row else row.get("Rating") if "Rating" in row else row.get("ratings", None),
            "reviews_text": row.get("reviews_text") or row.get("reviews") or row.get("reviews_texts", ""),
            "address": row.get("address") or row.get("formatted_address", ""),
            "time": row.get("time") or row.get("opening_hours", "")
        })
    return items

def main():
    parser = argparse.ArgumentParser(description="Sistem Rekomendasi Wisata Malang (Divide & Conquer)")
    parser.add_argument("--file", "-f", default=DEFAULT_EXCEL, help="Excel dataset path")
    parser.add_argument("--lat", type=float, required=False, help="Latitude user (jika tidak disediakan, akan diminta input)")
    parser.add_argument("--lng", type=float, required=False, help="Longitude user (jika tidak disediakan, akan diminta input)")
    parser.add_argument("--query", "-q", type=str, required=False, help="Kata kunci pencarian (contoh: 'pemandangan city light')")
    parser.add_argument("--max_distance", type=float, default=100.0, help="Max distance (km)")
    parser.add_argument("--min_rating", type=float, default=0.0, help="Min rating")
    parser.add_argument("--topk", type=int, default=20, help="Jumlah rekomendasi teratas")
    args = parser.parse_args()

    df = load_data(args.file)
    items = df_to_items(df)

     # === Ambil lokasi user ===
    if args.lat is None or args.lng is None:
        print("Mendeteksi lokasi otomatis melalui IP...")
        g = geocoder.ip('me')
        if g.ok and g.latlng:
            args.lat, args.lng = g.latlng
            print(f"Lokasi berhasil terdeteksi: lat={args.lat}, lng={args.lng}")
        else:
            print("Gagal mendeteksi lokasi otomatis. Masukkan koordinat manual.")
            args.lat = float(input("Masukkan lat (contoh -7.98): ").strip())
            args.lng = float(input("Masukkan lng (contoh 112.63): ").strip())

    # === Input kata kunci ===
    if not args.query:
        args.query = input("Masukkan kata kunci (contoh 'pemandangan city light'): ").strip()

    print(f"\nMemproses dataset ({len(items)} destinasi) ...")
    # jalankan DAC
    results = divide_and_conquer(items, user_lat=args.lat, user_lng=args.lng, query=args.query,
                                 max_distance_km=args.max_distance, min_rating=args.min_rating,
                                 chunk_size=50, top_k=args.topk)

    if not results:
        print("Tidak ditemukan rekomendasi yang cocok dengan filter Anda.")
        return

    print("\n=== Rekomendasi Teratas ===")
    for i, r in enumerate(results, start=1):
        print(f"{i}. {r['name']}  | rating: {r['rating']} | jarak: {r['distance_km']} km")
        print(f"   alamat: {r.get('address','-')} | jam buka: {r.get('opening_hours','-')}")
    print("\nSelesai.")

if __name__ == "__main__":
    main()
