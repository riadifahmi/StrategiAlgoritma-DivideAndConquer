LANGKAH PEMROSESAN DAN MENJALANKAN PROGRAM

1. Instalasi Modul yang Diperlukan
Sebelum menjalankan sistem, pastikan semua library Python yang dibutuhkan sudah terinstal.
Buka terminal di folder proyek (pastikan virtual environment sudah aktif, ditandai dengan (venv)), lalu jalankan perintah berikut:

//opsi 1
pip install pandas numpy openpyxl python-Levenshtein geocoder haversine
//opsi 2
py -m pip install pandas numpy openpyxl python-Levenshtein geocoder haversine

2. Menjalankan Program Utama
Jalankan file utama main.py dengan perintah berikut di terminal:

//opsi 1
python src/main.py -f data/Scraping_Clustering_Wisata_Malang.xlsx
//opsi 2
py src/main.py -f data/Scraping_Clustering_Wisata_Malang.xlsx

3. Alur Pemrosesan Sistem
Setelah perintah dijalankan, sistem akan melakukan tahapan sebagai berikut:
a. Mendeteksi koordinat pengguna secara otomatis menggunakan library geocoder melalui alamat IP perangkat.
b. Meminta input kata kunci destinasi wisata dari pengguna.
c. Membersihkan data teks (menghapus karakter aneh, simbol, dan emoticon yang tidak diperlukan).
d. Memproses data menggunakan algoritma Divide and Conquer, dengan tahapan:
    > Memecah dataset menjadi beberapa subkelompok (divide)
    > Menyaring data sesuai kecocokan kata kunci pada nama dan ulasan tempat wisata (filter)
    > Menggabungkan hasil penyaringan (conquer)
    > Mengurutkan hasil berdasarkan prioritas berikut:
        1. Relevansi kata kunci (kecocokan input dengan nama/review)
        2. Rating tertinggi
        3. Jarak terdekat dari lokasi pengguna
e. Menampilkan hasil rekomendasi di terminal secara langsung.
