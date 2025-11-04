import json
import pandas as pd

# ==============================================
# 1️⃣ Divide and Conquer Search
# ==============================================
def divide_and_conquer_search(data, keyword):
    """
    Membagi data menjadi dua subset, mencari keyword secara rekursif,
    lalu menggabungkan hasilnya menjadi satu daftar rekomendasi.
    """
    if len(data) <= 1:
        return data

    mid = len(data) // 2
    left = data[:mid]
    right = data[mid:]

    left_result = divide_and_conquer_search(left, keyword)
    right_result = divide_and_conquer_search(right, keyword)

    def keyword_match(item):
        name = str(item.get("name", "")).lower()
        review = str(item.get("reviews_text", "")).lower()
        return keyword.lower() in name or keyword.lower() in review

    filtered_left = [i for i in left_result if keyword_match(i)]
    filtered_right = [i for i in right_result if keyword_match(i)]

    return filtered_left + filtered_right


# ==============================================
# 2️⃣ Sistem Rekomendasi
# ==============================================
def recommend_places(keyword, top_n=10):
    # Baca data bersih hasil preprocessing
    with open("data/clean_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    matched_data = divide_and_conquer_search(data, keyword)

    if not matched_data:
        print(f"\n❌ Tidak ditemukan hasil untuk kata kunci '{keyword}'.")
        return

    df = pd.DataFrame(matched_data)

    # Urutkan hasil berdasarkan rating (desc) dan jarak (asc)
    df_sorted = df.sort_values(by=["rating", "distance_km"], ascending=[False, True]).head(top_n)

    # Tampilkan hasil
    print("\n===== HASIL REKOMENDASI =====")
    for _, row in df_sorted.iterrows():
        print(f"\nNama Tempat     : {row['name']}")
        print(f"Alamat          : {row['address']}")
        print(f"Rating          : {row['rating']}")
        print(f"Jarak dari Malang : {row['distance_km']} km")
        print(f"Ulasan Singkat  : {row['reviews_text'][:150]}...")
        print(f"Kategori        : {', '.join(row['types']) if isinstance(row['types'], list) else row['types']}")
    print("\n=============================\n")

    # Simpan hasil ke CSV
    df_sorted.to_csv("data/rekomendasi_hasil.csv", index=False, encoding="utf-8-sig")
    print("📄 Hasil rekomendasi disimpan di data/rekomendasi_hasil.csv")


# ==============================================
# 3️⃣ Main Program
# ==============================================
if __name__ == "__main__":
    print("=== Sistem Rekomendasi Wisata Malang ===")
    keyword = input("Masukkan kata kunci (contoh: 'cafe murah', 'pemandangan city light'): ").strip()
    recommend_places(keyword)
