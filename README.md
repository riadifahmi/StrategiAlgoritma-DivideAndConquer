# 🧭 Langkah Pemrosesan dan Menjalankan Program

## 1. Instalasi Modul yang Diperlukan
Sebelum menjalankan sistem, pastikan semua library Python yang dibutuhkan sudah terinstal.  
Buka terminal di folder proyek (pastikan **virtual environment** sudah aktif, ditandai dengan `(venv)`), lalu jalankan salah satu perintah berikut:

```bash
# Opsi 1
pip install pandas numpy openpyxl python-Levenshtein geocoder haversine

# Opsi 2
py -m pip install pandas numpy openpyxl python-Levenshtein geocoder haversine

```
## 2. Menjalankan Program Utama
Jalankan file utama main.py dengan perintah berikut di terminal:

```bash
# Opsi 1
python src/main.py -f data/Scraping_Clustering_Wisata_Malang.xlsx

# Opsi 2
py src/main.py -f data/Scraping_Clustering_Wisata_Malang.xlsx

```

## 3. Alur Pemrosesan Sistem
Setelah perintah dijalankan, sistem akan melakukan tahapan berikut:

1. Mendeteksi **koordinat pengguna** secara otomatis menggunakan library `geocoder` melalui alamat IP perangkat.  
2. Meminta **input kata kunci** destinasi wisata dari pengguna.  
3. Melakukan **pembersihan data teks** (menghapus karakter aneh, simbol, dan emoticon yang tidak diperlukan).  
4. Memproses data menggunakan algoritma **Divide and Conquer**, dengan tahapan:

   - 🔹 **Divide:** Memecah dataset menjadi beberapa subkelompok.  
   - 🔹 **Filter:** Menyaring data sesuai kecocokan kata kunci pada nama dan ulasan tempat wisata.  
   - 🔹 **Conquer:** Menggabungkan hasil penyaringan.  
   - 🔹 **Sort:** Mengurutkan hasil berdasarkan prioritas berikut:
     
        1. Relevansi kata kunci (kecocokan input dengan nama/review)  
        2. Rating tertinggi  
        3. Jarak terdekat dari lokasi pengguna  

5. Menampilkan hasil rekomendasi di **terminal** secara langsung.
