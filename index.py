# Data wisata (contoh sederhana)
wisata_malang = [
    {"nama": "Jatim Park 1", "kategori": "taman hiburan", "rating": 4.5, "jarak": 5},
    {"nama": "Museum Angkut", "kategori": "museum", "rating": 4.7, "jarak": 4},
    {"nama": "Coban Rondo", "kategori": "air terjun", "rating": 4.6, "jarak": 15},
    {"nama": "Batu Night Spectacular", "kategori": "taman hiburan", "rating": 4.3, "jarak": 6},
    {"nama": "Alun-Alun Malang", "kategori": "taman kota", "rating": 4.2, "jarak": 2},
    {"nama": "Coban Talun", "kategori": "air terjun", "rating": 4.5, "jarak": 14},
]

# Divide and Conquer
def cari_wisata(data, keyword, min_rating, max_jarak):
    if not data:
        return []

    if len(data) == 1:
        item = data[0]
        if (keyword.lower() in item["kategori"].lower() or keyword.lower() in item["nama"].lower()) \
           and item["rating"] >= min_rating \
           and item["jarak"] <= max_jarak:
            return [item]
        else:
            return []

    mid = len(data) // 2
    left = cari_wisata(data[:mid], keyword, min_rating, max_jarak)
    right = cari_wisata(data[mid:], keyword, min_rating, max_jarak)

    return left + right

# Main logic
keyword = input("Masukkan kata kunci (contoh: air terjun, taman, museum): ")
min_rating = float(input("Minimal rating (contoh: 4.0): "))
max_jarak = float(input("Maksimal jarak dari lokasi kamu (km): "))

hasil = cari_wisata(wisata_malang, keyword, min_rating, max_jarak)

# Sort berdasarkan rating tertinggi atau jarak terdekat
hasil = sorted(hasil, key=lambda x: (-x["rating"], x["jarak"]))

# Output
if hasil:
    print("\nRekomendasi wisata untuk kamu:")
    for w in hasil:
        print(f"- {w['nama']} | {w['kategori']} | Rating: {w['rating']} | Jarak: {w['jarak']} km")
else:
    print("\nTidak ada wisata yang sesuai dengan kriteria kamu.")
