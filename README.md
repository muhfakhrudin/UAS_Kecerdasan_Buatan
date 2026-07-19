# 📱 Smart IRecom — AI-Powered iPhone Recommender System

Smart IRecom adalah aplikasi sistem rekomendasi iPhone bekas yang ditenagai oleh algoritma pencarian probabilistik **Okapi BM25**. Aplikasi ini memproses data katalog dari marketplace Shopee dan Tokopedia, lalu meranking produk berdasarkan relevansi teks pencarian pengguna (seperti varian, kapasitas penyimpanan, battery health, wilayah toko, dan nama toko) secara real-time.

---

## 🚀 Prasyarat Sistem
Pastikan perangkat Anda sudah terinstal:
- **Python 3.12 ke atas**
- **Django 6.0** (Akan diinstal via virtual environment)

---

## 🛠️ Langkah Instalasi & Persiapan

Aplikasi tidak menyertakan virtual environment agar ukuran berkas penyerahan tetap ringkas. Ikuti langkah di bawah ini untuk membuat environment lokal dan menjalankannya.

### 1. Masuk ke Direktori Project
Buka terminal (CMD / PowerShell / Bash) lalu arahkan ke folder utama project:
```bash
cd "d:\KULYAH\Semester 6\Kecerdasan Buatan\smart_irecom"
```

### 2. Buat dan Aktifkan Virtual Environment (Windows)
Buat environment sekali saja:

```powershell
python -m venv venv
```

Lalu aktifkan `venv` sesuai shell yang Anda gunakan:

- **Menggunakan PowerShell (Direkomendasikan):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
  *(Catatan: Jika muncul error permission, jalankan perintah `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` terlebih dahulu)*

- **Menggunakan Command Prompt (CMD):**
  ```cmd
  .\venv\Scripts\activate.bat
  ```

- **Menggunakan Git Bash / WSL / Linux:**
  ```bash
  source venv/bin/activate
  ```

Setelah aktif, nama `(venv)` akan muncul di ujung kiri baris perintah terminal Anda.

### 3. Masuk ke Direktori Django
Navigasikan terminal Anda ke folder aplikasi Django tempat file `manage.py` berada:
```bash
cd SmartIrecom
```

### 4. Instalasi Dependensi
Install package yang diperlukan aplikasi:
```bash
pip install -r requirements.txt
```

---

## 🏃 Run Aplikasi (Operasional)

### 1. Jalankan Sistem Check
Pastikan konfigurasi aplikasi Django Anda tidak memiliki error:
```bash
python manage.py check
```

Jika database belum ada atau dijalankan pada komputer baru, buat tabel bawaan Django sekali saja:
```bash
python manage.py migrate
```

### 2. Mulai Development Server
Jalankan server lokal Django dengan perintah berikut:
```bash
python manage.py runserver
```
Setelah server berjalan, buka web browser pilihan Anda dan akses URL berikut:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🧪 Cara Pengujian & Uji Coba

### Menguji Halaman Pencarian AI
1. Di halaman utama, Anda akan melihat kotak pencarian modern dengan efek glow.
2. Coba masukkan query pencarian spesifik, contohnya:
   - `iPhone 11 Pro Max 256GB`
   - `iPhone 12 Tokopedia Jakarta`
   - `iPhone 13 battery health 90`
3. Klik tombol **Search with AI** atau tekan **Enter**.
4. Halaman hasil pencarian akan menampilkan:
   - **Database Scanned**: Jumlah produk yang berhasil discan.
   - **BM25 Execution Latency**: Kecepatan pemrosesan algoritma (dalam detik).
   - **Match Score & Visual Bar**: Nilai relevansi kuantitatif BM25 untuk masing-masing listing.
   - **Keyword Highlighting**: Kata kunci pencarian Anda yang cocok akan disorot dengan warna **neon cyan**.

### Menjalankan Automated Tests
Gunakan perintah internal Django untuk melakukan pengujian sistem:
```bash
python manage.py test
```

---

## 📂 Struktur Data & File Penting

- 📄 `dataset_iphone.csv`: Kumpulan data iPhone bekas dari marketplace yang berisi kolom: `Toko`, `Platform`, `Kategori Seri`, `Kategori Varian`, `penyimpanan`, `Battery Health`, `Harga`, `Pembayaran`, `Wilayah Toko`, `Kategori iPhone`.
- 📁 `recommender/search_engine.py`: Implementasi rumus matematika Okapi BM25, pembobotan IDF (Inverse Document Frequency), tokenisasi query, dan scoring teks.
- 📁 `recommender/views.py`: Logic pemrosesan request pencarian, pembersihan query, tracking waktu eksekusi, serta logika *neon keyword highlighting*.
- 📁 `recommender/templates/recommender/search.html`: Desain antarmuka responsif premium bergaya Glassmorphism dengan Tailwind CSS.

---

## ⚠️ Troubleshooting (Pecahkan Masalah)

- **Error: "ModuleNotFoundError: No module named 'django'"**
  > **Solusi:** Virtual environment belum diaktifkan. Ulangi langkah aktivasi `venv` pada bagian **Langkah 2** di atas sebelum menjalankan server.
  
- **Error: "Port 8000 is already in use"**
  > **Solusi:** Jalankan server pada port alternatif, misalnya port 8080:
  > ```bash
  > python manage.py runserver 8080
  > ```
