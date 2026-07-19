# CATATAN REVISI (baca dulu sebelum menyalin ke template IEEE)

Dokumen ini adalah **hasil audit + revisi langsung** terhadap draft paper asli Anda (`Draft_Perancangan...Second.md`). Prinsip kerja: tidak ada asumsi, tidak ada angka contoh, tidak ada hasil evaluasi fiktif. Semua bagian yang butuh hasil implementasi/eksperimen nyata ditandai placeholder eksplisit.

## Apa yang diubah, dan kenapa

1. **Framework aplikasi (Bab IV-A)**: draft asli menyebut **Streamlit**, bukan Django. Anda mengonfirmasi framework yang benar adalah **Django** — kemungkinan draft ini adalah versi lama dari fase UTS sebelum migrasi. Sudah diperbaiki, ditandai untuk verifikasi ulang saat audit source code (Tahap 3) supaya detail teknis (nama modul, struktur app) benar-benar cocok.
2. **Angka hasil evaluasi (85%–92% presisi) di Bab IV-D dan Kesimpulan**: draft asli sudah mencantumkan angka spesifik ini, tetapi tidak ada implementasi metrik evaluasi maupun eksperimen TF-IDF yang terverifikasi mendukungnya. Sesuai instruksi Anda ("jangan mengklaim implementasi yang belum diverifikasi", "jangan membuat hasil evaluasi fiktif"), angka ini **dihapus dan diganti placeholder**. Ini bukan penghapusan hasil kerja Anda — ini mencegah risiko akademik (dianggap memalsukan data eksperimen) sebelum eksperimen sungguhan dijalankan.
3. **Bab IV-E Perbandingan Metode**: draft asli membandingkan BM25 secara teoretis dengan "pencarian kata kunci murni" dan "TF klasik", bukan dengan **TF-IDF + Cosine Similarity** yang sudah disepakati sebagai baseline resmi. Diganti struktur baru dengan placeholder untuk tabel hasil nyata.
4. **Gaya sitasi**: Bab II (Tinjauan Pustaka) menulis sitasi gaya APA — "(Diningrat et. al., 2025)" — padahal pedoman dosen mewajibkan gaya IEEE bernomor `[1]`. Sudah dikonversi ke `[n]` sesuai nomor di Daftar Pustaka.
5. **Tabel I baris ke-3**: kolom nama peneliti kosong. Diisi "M. Agustina, Y. Azhar, dan N. Hayatin" — ini bukan tebakan, melainkan dicocokkan langsung dari Referensi [3] yang membahas judul dan topik identik di dokumen yang sama.
6. **Duplikasi rumus TF-IDF/BM25**: penjelasan rumus TF-IDF dan BM25 muncul dua kali hampir identik — sekali di Bab II (Landasan Teori) dan sekali lagi di Bab III (AI Mechanism). Sesuai pedoman, penjelasan detail rumus/parameter/contoh kerja seharusnya ada di **AI Mechanism (Bab III)**, sementara Bab II cukup sintesis literatur. Duplikasi di Bab II dihapus, isinya dipertahankan penuh di Bab III.
7. **Rumus matematika hilang**: file `.md` hasil konversi dari `.docx` kehilangan seluruh notasi matematika (kemungkinan rumus di dokumen asli berupa objek Equation Editor/gambar yang tidak ter-convert ke teks). Rumus di bawah ini saya rekonstruksi menggunakan notasi standar TF-IDF/BM25 yang konsisten dengan teks naratif di sekitarnya (bukan rumus baru) — **tetap wajib dicek ulang terhadap tampilan asli di file .docx/PDF Anda** untuk memastikan notasi persis sama.
8. **Placeholder template yang belum dihapus**: ditemukan dua sisa teks instruksi bawaan template IEEE yang belum dihapus — `Keywords-component, formatting, style, styling, insert (key words)` dan `Identify applicable funding agency here. If none, delete this text box.` Pedoman eksplisit melarang ini. Sudah dihapus/diisi.
9. **Caption gambar**: draft asli pakai "Gambar 1", "Gambar 2" — pedoman mewajibkan format `Fig. 1`, `Fig. 2`. Sudah diperbaiki.
10. **Heading Bab V**: draft asli memakai heading "Solusi" — pedoman mewajibkan heading bernomor Romawi `V. CONCLUSION`/kesimpulan. Sudah diperbaiki jadi "V. KESIMPULAN".
11. **Baris rusak di Daftar Pustaka**: ada baris aneh `[1], [2], [3]...[10]` tepat di bawah heading References (kemungkinan sisa field code reference manager yang tidak ter-resolve). Dihapus.
12. **Referensi kurang dari jumlah wajib (12–15) dan tidak selaras dengan Tabel I**: Daftar Pustaka asli hanya memuat 10 entri bernomor, sementara Tabel I mereferensikan 15 penelitian. Delapan penelitian di Tabel I (baris 6, 7, 8, 11, 12, 13, 14, 15) **tidak punya entri di Daftar Pustaka** — ini pelanggaran langsung terhadap pedoman ("semua sitasi harus muncul di daftar pustaka"). Saya berhasil memverifikasi **satu** sumber secara online dan menambahkannya sebagai referensi baru [11] (lihat Bagian References). **Tujuh sisanya tidak dapat saya tambahkan** karena saya tidak menemukan detail bibliografi (jurnal/volume/tahun/DOI) yang bisa diverifikasi secara online dengan yakin — menambahkan tanpa verifikasi berisiko mengarang sitasi. Mohon tim melampirkan detail lengkap dari sumber yang sudah dikumpulkan saat riset Tabel I (baris: Jain & Vashisht; Haikal, Rachmawati, Aris; Anan et al.; Lin & Huang; da Cruz & Hansun; Nafian et al.; Syaichudin et al.).
13. **Perbaikan bahasa**: sejumlah typo dan kalimat janggal diperbaiki tanpa mengubah makna (mis. "pengunna"→"pengguna", "algortima"→"algoritma", kalimat Abstract "memberikan data yang bias" diperbaiki jadi "data yang tidak bias dan transparan" — karena kalimat aslinya kontradiktif dengan tujuan penelitian yang justru ingin *mengatasi* bias).
14. **Acknowledgment ditambahkan**: pedoman mewajibkan disclosure jika AI generatif dipakai membantu penulisan. Ditambahkan draft kalimat standar — sesuaikan dengan penggunaan aktual tim.

## Update — Hasil Evaluasi Nyata Sudah Diisi (v2)

Aplikasi Django sudah berjalan dan memiliki fitur evaluasi live (`/evaluasi/` dan `/evaluasi/paper/`) hasil implementasi Tahap 4–6. Semua placeholder evaluasi di bawah sekarang diisi dengan angka **nyata** yang saya ambil langsung dari aplikasi yang berjalan (bukan dikarang):

- **Sumber angka resmi (Table II)**: halaman `/evaluasi/paper/` — 14 kueri uji berlabel, K=10, dijalankan atas 526 produk asli. Halaman ini eksplisit menyatakan angkanya dihitung live setiap kali dimuat, sumber logika sama persis dengan `python manage.py run_evaluation`, tidak ada angka yang di-cache/dikarang.
- **Sanity check tambahan**: saya juga menjalankan 3 kueri bebas pilihan saya sendiri (di luar 14 kueri resmi) lewat halaman `/evaluasi/` untuk memastikan pola hasil (BM25 ≥ TF-IDF) konsisten dan bukan kebetulan hasil kurasi 14 kueri resmi. Hasilnya konsisten — lihat catatan di Bab IV-E.
- **Catatan yang WAJIB diverifikasi tim saat audit source code (Tahap 1/3)**:
  - Jumlah produk berbeda 1 antara halaman utama ("527 Products") dan halaman evaluasi ("526 produk asli") — kemungkinan satu baris dataset di-drop di jalur evaluasi (mis. baris dengan atribut tak lengkap). Perlu dikonfirmasi ke source code, bukan ditebak.
  - Pada kueri tanpa atribut terstruktur (mis. "iphone second murah dibawah 3 juta"), TF-IDF+Cosine mengembalikan **0 hasil** sementara BM25 tetap mengembalikan 10 hasil dengan skor sangat rendah (0.0014–0.0016). Ini saya laporkan apa adanya sebagai observasi — penyebab pastinya (apakah TF-IDF punya threshold minimum similarity, penanganan vocabulary kosong, dsb.) perlu dicek di kode saat Tahap 3, bukan diasumsikan.

## Update — Verifikasi Visual Langsung terhadap Screenshot Docx Asli (v3)

Anda mengirim screenshot isi `.docx` asli. Ini memungkinkan verifikasi langsung (bukan rekonstruksi) terhadap rumus dan diagram, dengan temuan berikut:

1. **Rumus BM25 utama (Score/RSV) — CONFIRMED SAMA PERSIS** dengan rekonstruksi saya. Tidak perlu diubah.
2. **Rumus IDF di dalam BM25 — PERLU DIKOREKSI.** Paper asli menulis: `IDF(qi) = log((N − df(qi) + 0.5) / (df(qi) + 0.5))` — **tanpa "+1"** di akhir. Draft revisi saya sebelumnya menambahkan "+1" (varian smoothing ala Lucene/Elasticsearch modern), yang ternyata BUKAN yang tertulis di paper Anda. Sudah dikoreksi mengikuti rumus asli paper (prinsip: kode/paper mengikuti spesifikasi yang sudah ada, bukan versi "lebih baik" versi saya). **Catatan teknis untuk diverifikasi saat audit kode**: varian tanpa "+1" ini bisa menghasilkan IDF negatif untuk term yang muncul di lebih dari separuh dokumen korpus (df > N/2) — perlu dicek apakah source code menangani kasus ini (clamp ke 0, dsb.) atau membiarkannya apa adanya.
3. **Rentang standar k1 ditemukan eksplisit di paper**: 1,2 ≤ k1 ≤ 2 (ditambahkan ke penjelasan parameter).
4. **Inkonsistensi notasi internal pada rumus TF-IDF** (ditemukan di paper asli, bukan asumsi): rumus IDF berdiri sendiri ditulis `IDF(word) = log(td/df)` (pakai simbol *td*), tetapi rumus gabungan tepat di bawahnya ditulis `TF-IDF(t,d) = TF(t,d) × log(N/df_t)` (pakai simbol *N*) — untuk konsep yang identik (jumlah total dokumen). Ini inkonsistensi penulisan di paper asli Anda sendiri, sudah diseragamkan ke simbol *N* di draft revisi (konsisten dengan notasi BM25 di bagian selanjutnya).
5. **Gambar 1 & Gambar 2 — TERNYATA TIDAK PERLU DIGAMBAR ULANG.** Setelah melihat langsung, Gambar 2 (diagram alur bisnis sistem) berisi 6 langkah spesifik yang sudah sesuai dengan aplikasi yang saya konfirmasi berjalan sebelumnya: Input User (Kata Kunci & Filter) → Mesin AI (BM25) → Penyaringan (buang di luar rentang harga/baterai) → Pengurutan (harga/relevansi) → Tampilan UI (Top-15) → Aksi User (modal struk detail). Tidak generik, tidak menyebut Streamlit. **Rekomendasi diperbarui: pakai gambar aslinya, cukup ganti caption dari "Gambar 1/2" menjadi "Fig. 1/Fig. 2"** sesuai format IEEE — rekomendasi "gambar ulang di draw.io" sebelumnya saya tarik untuk kedua diagram ini.
6. **Yang tetap perlu dibuat baru**: diagram untuk fitur perbandingan BM25 vs TF-IDF (`/evaluasi/`) — dipastikan tidak ada di paper manapun karena fitur ini baru ada setelah draft ditulis.

## Yang TIDAK saya ubah
Tema penelitian, studi kasus, metode utama (BM25), baseline pembanding (TF-IDF+Cosine), judul, daftar anggota, kasus penggunaan (iPhone bekas, Tokopedia/Shopee), serta seluruh isi Bab III yang sudah baik (Case Study, Dataset Plan, System Requirement, Architecture/Flowchart narasi) dipertahankan.

---
---

# Perancangan Kecerdasan Buatan Menggunakan Metode _Term Frequency Saturation_ dengan Algoritma Okapi _Best Matching_ (BM25): Program Rekomendasi iPhone Bekas (_iRecom Master_)

Andri Darmawan
Departemen Program Pendidikan Informatika
Universitas Internasional Semen Indonesia, Kabupaten Gresik, Indonesia
<andri.darmawan23@student.uisi.ac.id>

Muhammad Awaludin Ikbar
Departemen Program Pendidikan Informatika
Universitas Internasional Semen Indonesia, Kabupaten Gresik, Indonesia
<muhammad.ikbar24@student.uisi.ac.id>

Muhammad Fakhruddin
Departemen Program Pendidikan Informatika
Universitas Internasional Semen Indonesia, Kabupaten Gresik, Indonesia
<muhammad.fakhruddin23@student.uisi.ac.id>

Novanda Hutomo Syah Putra
Departemen Program Pendidikan Informatika
Universitas Internasional Semen Indonesia, Kabupaten Gresik, Indonesia
<novanda.putra24@student.uisi.ac.id>

Rasendriyo Reswara Iriawanto
Departemen Program Pendidikan Informatika
Universitas Internasional Semen Indonesia, Kota Surabaya, Indonesia
<rasendriyo.iriawanto23@student.uisi.ac.id>

*Abstract*—Tingginya minat konsumen terhadap produk iPhone bekas (*second*) di Indonesia mendorong peningkatan transaksi pada platform marketplace seperti Tokopedia dan Shopee. Namun, keragaman penulisan teks deskripsi produk yang tidak terstruktur dan tidak homogen antar-penjual menyulitkan calon pembeli (*user*) dalam menemukan *smartphone* yang sesuai dengan preferensi spesifikasinya. Sistem pencarian bawaan konvensional sering kali bias terhadap dokumen teks yang panjang akibat manipulasi pengulangan kata kunci (*keyword stuffing*). Penelitian ini bertujuan untuk merancang sistem rekomendasi cerdas terpadu menggunakan algoritma Okapi BM25 — yang secara inheren menerapkan prinsip *term frequency saturation* — untuk mengatasi permasalahan tersebut. Dataset diperoleh melalui platform Tokopedia dan Shopee dengan pendekatan kualitatif untuk memetakan spesifikasi gawai bekas. Kinerja BM25 dibandingkan dengan baseline TF-IDF + Cosine Similarity menggunakan dataset, preprocessing, dan kueri uji yang identik. Hasil evaluasi terhadap 14 kueri uji berlabel pada 526 produk iPhone bekas asli menunjukkan Okapi BM25 unggul di seluruh metrik dibandingkan TF-IDF + Cosine Similarity (Precision@10 0,6071 vs 0,3214; Recall@10 0,7925 vs 0,5114; Hit Rate@10 1,0000 vs 0,9286; NDCG@10 0,9229 vs 0,4949), sekaligus dengan waktu komputasi rata-rata lebih cepat (10,92 ms vs 18,33 ms per kueri). Sistem ini terbukti dapat memberikan hasil pencarian yang lebih relevan dan transparan kepada calon pembeli, sekaligus mengoptimalkan efisiensi pengambilan keputusan pada pasar komoditas smartphone bekas.

**Keywords**—kecerdasan buatan, temu kembali informasi, sistem rekomendasi, Okapi BM25, TF-IDF

# I. PENDAHULUAN

Perkembangan teknologi informasi yang pesat telah mengubah lanskap perdagangan elektronik (*e-commerce*), termasuk pasar perangkat komunikasi pintar (*smartphone*). Sebagai salah satu produk elektronik dengan nilai jual tinggi, produk iPhone dengan kondisi bekas (*second*) tetap memiliki pangsa pasar yang sangat besar di Indonesia. Tingginya peminat iPhone di Indonesia didorong oleh keinginan pengguna untuk memiliki perangkat komunikasi pintar berkualitas tinggi dengan harga yang lebih terjangkau. Hingga saat ini, aktivitas transaksi jual-beli gawai bekas banyak berpusat pada platform toko daring (*marketplace*) besar di Indonesia seperti Tokopedia dan Shopee. Meskipun platform-platform tersebut menyediakan kemudahan akses, variabilitas data produk iPhone bekas yang ditawarkan sangat tinggi dan tersebar secara acak (*random*) di berbagai toko daring. Berbeda dengan gawai baru yang spesifikasinya seragam, produk iPhone bekas memiliki karakteristik unik yang tidak homogen. Setiap unit produk memiliki kondisi fisik, platform situs, kategori seri iPhone, kategori varian, tingkat kesehatan baterai (*Battery Health*), dan harga yang bervariasi tergantung kebijakan masing-masing penjual.

Melimpahnya opsi pemilihan data lintas platform ini sering kali menimbulkan ambiguitas dan kesulitan bagi calon pembeli untuk menyaring serta membandingkan produk secara objektif guna menemukan tipe yang paling sesuai dengan kebutuhan pengguna. Sistem pencarian bawaan dari situs toko daring saat ini juga umumnya masih berbasis kata kunci (*keyword-based search*) konvensional yang kaku, sehingga tidak mampu memberikan rekomendasi personal berdasarkan kedekatan preferensi multi-atribut yang diinginkan oleh pengguna.

Kondisi nyata pada proses pencarian komoditas gawai bekas saat ini masih menghadapi kendala teknis yang signifikan akibat tidak seragamnya tampilan deskripsi dan informasi yang diberikan oleh pihak penjual. Sebagian penjual memberikan informasi penting seperti tingkat kesehatan baterai (*battery health*) dan kelengkapan unit secara singkat, sementara sebagian penjual memberikan deskripsi yang panjang dan ambigu dengan pengulangan kata kunci yang berlebihan — kondisi yang secara teknis dikenal sebagai *keyword stuffing* dan menjadi kelemahan utama metode pembobotan berbasis frekuensi kata linear seperti TF-IDF.

Berdasarkan tinjauan atas penelitian terdahulu (dibahas lengkap pada Bab II), belum ada penelitian yang menerapkan algoritma Okapi BM25 secara spesifik pada konteks *marketplace* jual-beli gawai bekas, dan belum ada penelitian pada domain ini yang membandingkan kinerjanya secara terukur terhadap baseline TF-IDF + Cosine Similarity menggunakan dataset yang identik. Penelitian ini bertujuan untuk: (1) merancang dan mengimplementasikan sistem rekomendasi berbasis BM25 untuk pencarian iPhone bekas lintas marketplace, (2) mengimplementasikan TF-IDF + Cosine Similarity sebagai baseline pembanding menggunakan dataset dan preprocessing yang identik, dan (3) mengevaluasi serta membandingkan kinerja kedua metode menggunakan metrik yang sesuai untuk sistem rekomendasi berbasis teks. Kontribusi yang diharapkan dari penelitian ini adalah tersedianya bukti empiris mengenai keunggulan/kelemahan BM25 dibanding TF-IDF pada domain deskripsi produk marketplace bahasa Indonesia yang tidak terstruktur, serta perangkat lunak fungsional yang dapat diuji langsung oleh pengguna.

# II. TINJAUAN PUSTAKA

Penggunaan kecerdasan buatan untuk kebutuhan pencarian dan rekomendasi berkembang pesat dalam beberapa tahun terakhir. Berbagai penelitian memanfaatkan metode pembobotan statistik berbasis frekuensi kata — baik TF-IDF maupun Okapi BM25 — untuk memprediksi kedekatan pencarian dokumen atau kata kunci terdekat. Beberapa penelitian terdahulu yang relevan dengan penelitian ini dirangkum pada Tabel I.

TABLE I. PERBANDINGAN PENELITIAN TERDAHULU

| No | *Peneliti* | *Metode* | *Studi Kasus* | *Hasil/Temuan* |
|---|---|---|---|---|
| 1 | Diningrat et al. [6] | TF-IDF dan BM25 | Optimasi Algoritma Pencarian Dokumen Akademik | Algoritma BM25 memberikan kinerja yang lebih baik daripada TF-IDF |
| 2 | Simatupang et al. [4] | Text Mining dan TF-IDF | Analisa Testimonial Pada Toko Allmeeart | Algoritma text-mining dan TF-IDF mampu melakukan klasifikasi testimoni positif dan negatif |
| 3 | Agustina et al. [3] | Okapi BM25 | Sistem Rekomendasi Dosen Pembimbing Berdasarkan Relevansi Topik Tugas Akhir | Hasil akurasi kesesuaian sistem memberikan rekomendasi sebesar 65% |
| 4 | Darmawan et al. [5] | Okapi BM25 | Sistem Pencarian Informasi Berbasis Teks | BM25 menunjukkan kinerja yang secara konsisten lebih unggul dibandingkan TF dan TF-IDF |
| 5 | Baihaqi et al. [7] | TF-IDF dan Okapi BM25 | Temu Kembali Informasi pada Berita Olahraga Bahasa Indonesia | Penerapan BM25 dengan seleksi fitur TF dapat diterapkan pada sistem temu kembali informasi melalui pre-processing, penghitungan term frequency, penghapusan term bernilai rendah, pembobotan kata, penghitungan skor BM25, hingga pemeringkatan dokumen relevan |
| 6 | Jain & Vashisht [†] | Content-Based Filtering (CBF) dan Context-Based Filtering | Tinjauan umum teknik sistem rekomendasi lintas domain | CBF menggunakan atribut item untuk rekomendasi, namun terbatas dalam analisis konten dan menghadapi masalah pengguna baru (*cold start*) |
| 7 | Haikal, Rachmawati, & Aris [†] | Multi-Layer Perceptron (MLP) dengan BM25 dan TF-IDF | Klasifikasi kepuasan pelanggan aplikasi Livin' by Mandiri berdasarkan ulasan Google Play Store | MLP dengan BM25 menghasilkan akurasi tertinggi 88,4%, mengungguli TF-IDF (87,9%); BM25 lebih efektif untuk pembobotan fitur teks pada klasifikasi sentimen |
| 8 | Anan et al. [†] | Content-Based Filtering (CBF) dengan TF-IDF dan Cosine Similarity | Sistem rekomendasi produk pada platform e-commerce | CBF berhasil merekomendasikan produk relevan berdasarkan atribut produk (nama, kategori, harga); TF-IDF dan Cosine Similarity efektif mengukur kemiripan antar produk |
| 9 | Hernawan, Adikara, & Wihandika [9] | Algoritma TextRank dan BM25+ | Peringkasan artikel berita berbahasa Indonesia | Integrasi TextRank dan BM25+ menghasilkan ringkasan lebih koheren dan informatif dibanding TextRank saja, dengan peningkatan signifikan pada skor ROUGE |
| 10 | Hanan et al. [10] | Random Forest, Gradient Boosting, SVM, Regresi Linear, dan TF-IDF | Analisis harga dan dinamika ulasan listing iPhone di e-commerce India (Flipkart) | Brand, storage, dan rating signifikan memengaruhi harga; Random Forest memberikan akurasi prediksi harga terbaik; sentimen ulasan berkorelasi positif dengan rating produk |
| 11 | Lin & Huang [†] | Text mining dan Regresi | Pengaruh merek terhadap harga pasar barang bekas di Taiwan (platform Ruten) | Brand berpengaruh signifikan terhadap harga jual kembali; produk brand premium mempertahankan nilai jual lebih tinggi di pasar *second-hand* |
| 12 | Agustian, Hadiana, & Rahman [11] | TF-IDF dan Count Vectorization dengan Cosine Similarity | Sistem rekomendasi mobil listrik | TF-IDF lebih unggul dibanding Count Vectorization dengan rata-rata cosine similarity 0,299 vs 0,256 dalam merekomendasikan mobil listrik yang relevan |
| 13 | da Cruz & Hansun [†] | TF-IDF dengan SVM, Naive Bayes, dan Random Forest | Klasifikasi ulasan aplikasi Shopee di Google Play Store | SVM dengan TF-IDF menghasilkan akurasi tertinggi (87%), mengungguli Naive Bayes (83%) dan Random Forest (85%) |
| 14 | Nafian, Nugroho, & Musdholifah [†] | Okapi BM25 | Rekomendasi dosen pembimbing tugas akhir di Departemen TIEK UGM | Metode Okapi BM25 berhasil merekomendasikan dosen pembimbing berdasarkan kesesuaian topik tugas akhir dengan bidang keahlian dosen |
| 15 | Syaichudin, Mahmudy, & Suprapto [†] | TF-IDF | Analisis sentimen dari data web (big data) | Penerapan TF-IDF pada data hasil web scraping meningkatkan kualitas data dan akurasi analisis sentimen dengan mengurangi noise dari data mentah |

*[†] Sumber ini disebutkan dalam riset Tabel I namun entri lengkap di Daftar Pustaka belum dapat diverifikasi secara online oleh proses revisi ini — mohon tim melampirkan detail bibliografi asli (jurnal/prosiding, volume, tahun, DOI) agar dapat ditambahkan sebagai referensi bernomor yang sah.*

Berdasarkan tinjauan literatur di atas, masing-masing metode memiliki kelebihan dan kekurangan tersendiri. Okapi BM25 mampu menutupi kekurangan TF-IDF berkat fitur normalisasi panjang dokumen, sehingga lebih presisi untuk temu kembali informasi (*information retrieval*). Sayangnya, penggunaan BM25 selama ini masih didominasi oleh sistem pencarian dokumen akademik dan jarang diterapkan untuk rekomendasi produk marketplace.

Selain itu, penelitian terdahulu umumnya hanya membandingkan kinerja TF-IDF dan BM25 secara terpisah, atau menerapkannya pada domain lain (dokumen akademik, ulasan aplikasi, peringkasan berita). Belum ada penelitian pada konteks *marketplace* jual-beli gadget bekas yang membandingkan keduanya secara terukur pada dataset yang identik. Riset terkait pasar produk bekas (*second-hand*) yang ada, khususnya smartphone, juga masih sebatas analisis harga atau sentimen ulasan (baris 10, 11), bukan sistem rekomendasi berbasis teks.

Dengan demikian, kebaruan (*novelty*) penelitian ini terletak pada penerapan BM25 sebagai metode utama sistem rekomendasi teks pada studi kasus spesifik jual-beli iPhone bekas lintas marketplace Indonesia, dilengkapi dengan perbandingan empiris langsung terhadap baseline TF-IDF + Cosine Similarity menggunakan dataset, preprocessing, dan kueri uji yang identik — sesuatu yang belum dilakukan pada penelitian-penelitian sebelumnya.

# III. METODE PENELITIAN

## A. Studi Kasus (Case Study)

Sistem rekomendasi merupakan sebuah perangkat lunak yang dikembangkan untuk menyajikan saran atau rekomendasi kepada pengguna mengenai suatu produk. Pembuatan rekomendasi ini pada penelitian ini memanfaatkan prinsip pencocokan konten (kueri pengguna terhadap deskripsi produk), berbeda dengan pendekatan collaborative filtering yang bergantung pada riwayat transaksi atau rating pengguna lain.

Sistem temu kembali informasi (*information retrieval*) didefinisikan sebagai bidang ilmu untuk menemukan dokumen yang relevan di dalam koleksi data besar dan tidak terstruktur, guna memenuhi kebutuhan informasi pengguna. Pengguna memasukkan kueri (*query*) yang mewakili kebutuhan informasinya untuk diproses oleh mesin pencari (*search engine*). Fungsi utama mesin pencari adalah memahami maksud pengguna dan memberikan daftar hasil berperingkat berdasarkan nilai kedekatan relevansi tertinggi. Studi kasus penelitian ini adalah pencarian dan rekomendasi produk iPhone bekas pada data yang dikumpulkan dari marketplace Tokopedia dan Shopee.

## B. Pengumpulan Data dan Rencana Prapemrosesan (Dataset Collection and Preprocessing Plan)

Dataset aktual yang digunakan dalam penelitian ini merupakan data sekunder komoditas gawai bekas yang disatukan dalam format *Comma Separated Values* (CSV). Dataset ini memuat berbagai atribut teknis dan deskriptif mengenai stok iPhone bekas, meliputi nama produk, rentang harga, tingkat kesehatan baterai, serta teks deskripsi bebas dari penjual.

Sebelum diproses oleh algoritma pemeringkatan, dataset mentah melalui tahapan preprocessing ekstensif untuk menangani variabilitas data, ketiadaan nilai (*missing value*), serta gangguan tekstual (*noise*). Preprocessing dibagi menjadi dua alur utama, yaitu prapemrosesan atribut numerik-kategorikal dan prapemrosesan teks deskriptif:

- Pembersihan data (*data cleaning*) dan ekstraksi pada kolom harga dibersihkan dari karakter non-numerik agar dapat dikomputasi. Sistem menggunakan *Regular Expression* (Regex) untuk mengekstrak nilai kesehatan baterai secara otomatis dari teks deskripsi bebas.
- Imputasi data untuk mencegah hilangnya baris data berharga: nilai kesehatan baterai yang kosong diisi dengan nilai median dari keseluruhan dataset.
- Rekayasa fitur untuk mengelompokkan data spesifik menjadi kategori yang lebih terstruktur. Kolom seri dipetakan ke dalam "Kategori Seri" (misal: iPhone 11, iPhone 12) dan "Varian" (Pro Max, Pro, Mini, Biasa) guna mempermudah penyaringan awal (*hard-filtering*).
- Prapemrosesan teks (*text preprocessing*) untuk mengoptimalkan ekstraksi term pada deskripsi: teks diubah menjadi huruf kecil (*case folding*), dibersihkan dari tanda baca, dipisahkan menjadi unit kata (*tokenizing*), dihilangkan kata hubungnya (*stopword removal*), dan dikembalikan ke kata dasarnya (*stemming*).

**[Jumlah data aktual per sumber (Tokopedia/Shopee), jumlah baris sebelum-sesudah cleaning, dan contoh data mentah vs bersih akan diisi setelah audit source code dan dataset — lihat Bab IV-B]**

## C. Analisis Kebutuhan Sistem (System Requirement Analysis)

Pengembangan Sistem Rekomendasi iPhone Bekas ini memerlukan analisis menyeluruh terhadap kebutuhan fungsional maupun non-fungsional untuk memastikan sistem dapat menjalankan operasionalnya secara efektif sebagai mesin rekomendasi produk cerdas untuk pasar iPhone bekas di Indonesia.

*Kebutuhan Fungsional*

- **KF-1 (Pemrosesan Kueri Bahasa Alami):** Sistem harus mampu menerima masukan teks bebas dari pengguna dalam format campuran Bahasa Indonesia dan Bahasa Inggris, serta melakukan tokenisasi menjadi satuan kata yang dapat dicari menggunakan pemisahan batas alfanumerik.
- **KF-2 (Pemeringkatan Relevansi BM25):** Sistem harus mengimplementasikan fungsi pemeringkatan probabilistik Okapi BM25 untuk menghitung skor relevansi antara kueri pengguna dan daftar produk yang tersedia. Mekanisme penilaian ini menggunakan pembobotan *Inverse Document Frequency* (IDF) dengan saturasi frekuensi istilah (k₁ = 1,5) dan normalisasi panjang dokumen (b = 0,75) untuk mencegah bias terhadap deskripsi produk yang terlalu panjang.
- **KF-3 (Penyaringan Keras Multi-Kriteria):** Sistem harus mendukung filter parametrik pasca-penilaian yang mencakup: (a) rentang harga minimum dan maksimum dalam Rupiah, (b) persentase kesehatan baterai minimum dengan tingkatan yang telah ditentukan (≥80%, ≥90%, 100%), (c) pemilihan platform marketplace (Shopee atau Tokopedia), serta (d) kategori sertifikasi produk (Resmi atau Inter).

*Kebutuhan Non-Fungsional*

- **KNF-1 (Tanpa Dependensi Eksternal pada Inti AI):** Algoritma BM25 harus diimplementasikan hanya menggunakan modul pustaka standar Python (`math`, `re`, `collections`, `csv`) tanpa memerlukan kerangka kerja pembelajaran mesin pihak ketiga.
- **KNF-2 (Aksesibilitas):** Antarmuka sistem harus mendukung dua mode tampilan (tema terang dan gelap) dengan rasio kontras yang memenuhi standar WCAG.

*[Catatan revisi: KNF-1 menyatakan BM25 hanya memakai pustaka standar Python. Konsistensi ini perlu dijaga saat implementasi baseline TF-IDF + Cosine Similarity pada Tahap 4 — akan dikonfirmasi apakah tim ingin baseline pembanding memakai pendekatan manual serupa (tanpa scikit-learn) demi konsistensi metodologis, atau scikit-learn diperbolehkan khusus untuk baseline karena bukan bagian dari "inti AI" utama penelitian ini.]*

## D. Mekanisme Kecerdasan Buatan (AI Mechanism)

### D.1 Baseline Pembanding: Term Frequency – Inverse Document Frequency (TF-IDF)

TF-IDF merupakan metode pembobotan statistik klasik yang digunakan untuk menentukan seberapa penting suatu kata kunci (*term*) terhadap sebuah dokumen dalam suatu koleksi (korpus). Metode ini menggabungkan dua komponen:

Komponen *Term Frequency* (TF) menghitung berapa kali suatu term *t* muncul dalam dokumen *d*:

TF(*t*, *d*) = *f*(*t*, *d*)

dengan *f*(*t*, *d*) adalah jumlah kemunculan term *t* pada dokumen *d*.

Komponen *Inverse Document Frequency* (IDF) mengukur seberapa umum atau unik suatu term di seluruh korpus:

IDF(*t*) = log( *N* / *df*(*t*) )

dengan *N* adalah jumlah total dokumen dalam korpus dan *df*(*t*) adalah jumlah dokumen yang mengandung term *t*. Bobot akhir TF-IDF diperoleh dari perkalian kedua komponen:

TF-IDF(*t*, *d*) = TF(*t*, *d*) × log( *N* / *df*(*t*) )

Skor kemiripan antara kueri *Q* dan dokumen *D* pada baseline ini dihitung menggunakan *Cosine Similarity* antara vektor bobot TF-IDF kueri dan dokumen:

sim(*Q*, *D*) = ( **V**ᵩ · **V**_D ) / ( ‖**V**ᵩ‖ × ‖**V**_D‖ )

dengan **V**ᵩ dan **V**_D masing-masing adalah vektor bobot TF-IDF dari kueri dan dokumen.

*[Catatan revisi (terverifikasi langsung dari screenshot docx asli): rumus TF dan TF-IDF gabungan di atas sudah sama persis dengan paper asli. Satu perbaikan kecil diterapkan: paper asli menulis rumus IDF berdiri sendiri dengan simbol berbeda ("td" bukan "N") untuk konsep yang sama — sudah diseragamkan ke "N" agar konsisten dengan notasi BM25 di bagian D.2. Rumus Cosine Similarity belum ada di paper asli (baseline TF-IDF di paper asli hanya sampai pembobotan, belum ke skema ranking) — ditambahkan karena baseline pembanding butuh mekanisme ranking; wajib dicek terhadap implementasi kode aktual Tahap 4.]*

### D.2 Metode Utama: Algoritma Okapi Best Matching 25 (BM25)

Okapi *Best Matching* 25 (BM25) adalah algoritma pemeringkatan dokumen berbasis model probabilistik (*Probabilistic Retrieval Model*) yang digunakan untuk mesin pencarian. BM25 dikembangkan sebagai penyempurnaan dari metode heuristik TF-IDF klasik. Berbeda dengan TF-IDF, BM25 tidak mempertimbangkan frekuensi kata secara linear, melainkan menerapkan **saturasi frekuensi term** (*term frequency saturation*) — peningkatan skor akibat pengulangan kata semakin berkurang setelah melewati ambang tertentu — sekaligus turut memperhitungkan faktor panjang dokumen (*document length*).

Algoritma BM25 bekerja berdasarkan tiga komponen pembobotan: *inverse document frequency* (IDF), *term frequency* (TF) dengan saturasi, serta fungsi normalisasi panjang dokumen (*document length normalization*). Skor total relevansi atau *Retrieval Status Value* (RSV) suatu dokumen *D* terhadap kueri *Q* yang terdiri dari term *q₁, q₂, ..., qₙ* dirumuskan sebagai:

RSV(*D*, *Q*) = Σᵢ IDF(*qᵢ*) · [ *f*(*qᵢ*, *D*) · (k₁ + 1) ] / [ *f*(*qᵢ*, *D*) + k₁ · (1 − b + b · |*D*| / avgdl) ]

dengan komponen IDF dihitung menggunakan rumus model peluang berikut (varian klasik Robertson-Sparck Jones):

IDF(*qᵢ*) = log( (*N* − *df*(*qᵢ*) + 0,5) / (*df*(*qᵢ*) + 0,5) )

Keterangan:
- *N*: jumlah total dokumen dalam korpus.
- *df*(*qᵢ*): jumlah dokumen dalam koleksi yang mengandung term *qᵢ*.
- *f*(*qᵢ*, *D*): frekuensi kemunculan term *qᵢ* pada dokumen *D*.
- |*D*|: panjang dokumen *D* (jumlah kata di dalamnya).
- avgdl: rata-rata panjang dokumen di seluruh koleksi korpus.
- k₁: konstanta tuning saturasi frekuensi term, dengan rentang standar **1,2 ≤ k₁ ≤ 2**. Sesuai KF-2, nilai yang digunakan sistem ini adalah **k₁ = 1,5**.
- b: konstanta tuning normalisasi panjang dokumen, rentang standar **0 ≤ b ≤ 1**, umumnya bernilai 0,75. Sesuai KF-2, nilai yang digunakan sistem ini adalah **b = 0,75**.

*[Catatan revisi (terverifikasi langsung dari screenshot docx asli): rumus RSV utama dan seluruh keterangan di atas sudah sama persis dengan paper asli — tidak direkonstruksi ulang. Satu koreksi diterapkan dari draft v1: rumus IDF paper asli TIDAK memakai "+1" di akhir (varian klasik, bukan varian smoothing modern ala Lucene) — draft v1 saya sebelumnya keliru menambahkan "+1"; sudah diperbaiki mengikuti paper asli. Catatan teknis: varian tanpa "+1" ini bisa menghasilkan IDF negatif untuk term yang muncul di lebih dari separuh dokumen korpus (df > N/2) — perlu dicek saat audit source code (Tahap 1/3) apakah kode menangani kasus ini secara eksplisit. Nilai k₁=1,5 dan b=0,75 tetap perlu dikonfirmasi terhadap konstanta aktual di kode saat Tahap 3.]*

**[Contoh perhitungan RSV langkah-demi-langkah menggunakan satu kueri nyata dan 2–3 dokumen aktual dari dataset akan diisi setelah audit source code dan dataset — bertujuan membuktikan pemahaman tim atas mekanisme, bukan sekadar menjalankan library]**

## E. Arsitektur Sistem dan Diagram Alur (System Architecture and Flowchart)

Arsitektur sistem rekomendasi dirancang memproses kueri teks pengguna secara sekuensial, sebagaimana digambarkan pada Fig. 1. Alur dimulai dari validasi kueri beserta parameter filter harga dan filter kesehatan baterai, dilanjutkan dengan tokenisasi teks untuk pencocokan korpus. Sistem kemudian menghitung skor relevansi dokumen menggunakan algoritma Okapi BM25 dan menerapkan ambang batas (*threshold*) 10% untuk membuang produk yang tidak relevan. Produk yang lolos dievaluasi kembali melalui filter terperinci sesuai kriteria absolut, lalu diurutkan secara hierarkis untuk mengekstrak 15 kandidat terbaik. Hasil akhir disajikan pada antarmuka yang dilengkapi fitur penyorotan kata (*highlight*). Sebagai interaksi akhir, klik pada kartu produk memunculkan jendela *modal* berdimensi 4:3 (menyerupai struk digital) yang memuat rincian spesifikasi dan tautan menuju platform penjual.

**Fig. 1.** Diagram alur cara kerja sistem *[gambar asli sudah spesifik dan sesuai — cukup gunakan ulang gambar dari file docx sumber, ganti caption dari "Gambar 1" menjadi "Fig. 1". Tidak perlu digambar ulang.]*

Alur interaksi pengguna dengan program rekomendasi divisualisasikan secara ringkas pada Fig. 2. Proses diawali oleh pengguna yang memasukkan kata kunci pencarian beserta pengaturan parameter filter pendukung. Berdasarkan masukan tersebut, mesin kecerdasan buatan terintegrasi mencari tingkat kemiripan teks antara kueri dan korpus menggunakan algoritma pemeringkatan Okapi BM25. Sistem kemudian melakukan penyaringan otomatis untuk membuang produk yang berada di luar batas rentang harga maupun kapasitas baterai yang ditetapkan pengguna. Kandidat produk yang lolos saring selanjutnya diurutkan secara dinamis berdasarkan opsi yang dipilih pengguna — prioritas harga atau tingkat relevansi tertinggi. Setelah komputasi latar belakang selesai, antarmuka sistem menampilkan 15 produk gawai bekas terbaik sebagai rekomendasi utama. Pengguna dapat mengeklik salah satu produk untuk meninjau spesifikasi lebih mendalam melalui tampilan modal berformat struk detail.

**Fig. 2.** Diagram alur bisnis sistem — 6 langkah: Input User (Kata Kunci & Filter) → Mesin AI (pencarian kemiripan teks dengan Okapi BM25) → Penyaringan (buang produk di luar rentang harga/baterai) → Pengurutan (sesuai pilihan harga/relevansi) → Tampilan UI (Top-15 produk terbaik) → Aksi User (klik untuk lihat modal struk detail). *[gambar asli sudah spesifik, sesuai dengan aplikasi yang berjalan, dan tidak menyebut Streamlit — cukup gunakan ulang, ganti caption dari "Gambar 2" menjadi "Fig. 2". Tidak perlu digambar ulang.]*

**[Diagram baru yang masih perlu dibuat: alur fitur perbandingan BM25 vs TF-IDF (`/evaluasi/` dan `/evaluasi/paper/`) — belum ada di paper manapun karena fitur ini baru diimplementasikan setelah draft asli ditulis. Sarankan format serupa Fig. 1/2 (vertical flowchart berwarna) agar konsisten secara visual.]**

## F. Rencana Evaluasi dan Metode Pembanding

Evaluasi sistem dilakukan secara kuantitatif menggunakan pendekatan standar evaluasi *information retrieval* dan sistem rekomendasi, dengan rincian sebagai berikut:

- **Metode pembanding (baseline):** TF-IDF + Cosine Similarity (Bagian III.D.1), dijalankan pada dataset, tahapan preprocessing, dan kueri uji yang **identik** dengan BM25, agar perbandingan valid secara metodologis.
- **Query uji:** 14 kueri representatif yang mencakup variasi pencarian nyata pengguna (kombinasi seri/varian iPhone, kapasitas penyimpanan, platform, wilayah toko, dan tingkat kesehatan baterai), misalnya "iPhone 12 Pro 128GB Resmi" dan "iPhone 13 Pro battery diatas 90".
- **Ground truth:** relevansi ditentukan **deterministik**, bukan label manual subjektif — sebuah produk dianggap relevan terhadap suatu kueri jika ia memenuhi **seluruh** batasan eksplisit yang terkandung pada teks kueri (semantik AND), dicocokkan langsung terhadap atribut asli produk di dataset (`kategori_varian`, `penyimpanan`, `platform`, substring `wilayah_toko`, `kategori_iphone`, dan `battery_val` ≥ ambang batas). Pendekatan ini membuat ground truth dapat direproduksi penuh dari data yang sama, tanpa penilaian subjektif.
- **Metrik evaluasi wajib:** Precision@10, Recall@10, Hit Rate@10.
- **Metrik evaluasi opsional:** NDCG@10 — diimplementasikan dan disertakan karena memberi nilai tambah interpretasi (lihat Bab IV-D).
- **Metrik pendukung:** rata-rata waktu komputasi per kueri untuk kedua metode (K=10).

Hasil evaluasi aktual disajikan pada Bab IV-D dan IV-E, dihitung live oleh aplikasi (halaman `/evaluasi/paper/`) menggunakan logika yang sama persis dengan management command `python manage.py run_evaluation` — tidak ada angka yang di-cache atau dikarang.

# IV. HASIL DAN DISKUSI

## A. Implementasi Sistem

Sistem rekomendasi gawai bekas ini diimplementasikan sebagai perangkat lunak berbasis web menggunakan kerangka kerja **Django** (Python). *[Catatan revisi: draft asli menyebut kerangka kerja Streamlit — telah dikoreksi ke Django sesuai konfirmasi. Detail arsitektur app Django, nama modul, dan struktur front-end/back-end akan diverifikasi dan dilengkapi setelah audit source code pada Tahap 1–3.]*

Aplikasi memiliki tiga halaman utama yang telah diverifikasi berjalan nyata: (1) halaman pencarian utama dengan input kueri bebas, filter harga/kesehatan baterai/platform/tipe, dan mode tampilan terang-gelap (memenuhi KNF-2); (2) halaman **Bandingkan BM25 vs TF-IDF** (`/evaluasi/`) yang menjalankan kedua metode secara live atas kueri bebas pilihan pengguna; dan (3) halaman **Evaluasi Resmi** (`/evaluasi/paper/`) yang menyajikan hasil evaluasi 14 kueri berlabel sebagai acuan resmi Table II pada paper ini.

**Fig. 3.** Halaman pencarian utama iRecom Master *[screenshot sudah diambil selama sesi ini — sisipkan tangkapan layar aplikasi berjalan]*

**Fig. 4.** Halaman Evaluasi Resmi BM25 vs TF-IDF (`/evaluasi/paper/`) menampilkan Table II live *[screenshot sudah diambil selama sesi ini — sisipkan tangkapan layar]*

**[Screenshot hasil ranking dengan skor BM25 per produk dan halaman detail produk akan disisipkan sebagai Fig. 5 dst.]**

## B. Hasil Preprocessing

Proses pembersihan dan transformasi data diterapkan pada korpus utama yang bersumber dari berkas CSV. Hasil pemrosesan ini terbagi menjadi dua aspek:

- **Transformasi numerik dan kategorikal:** sistem berhasil mereduksi noise pada atribut harga dengan mengeliminasi string non-numerik (seperti "Rp" dan tanda titik ribuan). Implementasi *Regular Expression* (Regex) mengekstrak nilai kesehatan baterai yang tersembunyi di dalam teks deskripsi penjual secara otomatis. Untuk mencegah hilangnya baris data, sistem mengimputasi nilai median pada produk yang tidak mencantumkan informasi kesehatan baterai secara spesifik.
- **Transformasi tekstual:** teks deskripsi spesifikasi direduksi ke bentuk standar melalui case folding, penghapusan tanda baca, stopword removal, dan stemming. Tahapan ini memastikan algoritma terbebas dari bias akibat perbedaan gaya penulisan antar-penjual di berbagai marketplace.

Dataset akhir yang termuat di aplikasi berisi **526–527 produk** iPhone bekas nyata dari Shopee dan Tokopedia (`dataset_iphone.csv`) — terdapat selisih 1 produk antara jumlah yang ditampilkan di halaman utama (527) dan jumlah yang dipakai mesin evaluasi (526); penyebab selisih ini *[perlu dikonfirmasi saat audit source code Tahap 1 — kemungkinan satu baris dengan atribut tidak lengkap di-drop khusus di jalur evaluasi]*. **[Jumlah baris sebelum/sesudah cleaning, rata-rata panjang dokumen (avgdl), dan ukuran vocabulary akan diisi setelah audit source code langsung terhadap fungsi preprocessing]**

## C. Mekanisme BM25 pada Implementasi (Hasil Algoritma)

Proses pencocokan dan pemeringkatan dokumen dieksekusi secara terpusat menggunakan algoritma Okapi BM25 sesuai rumus pada Bagian III.D.2. Algoritma ini menghitung frekuensi kemunculan term (*term frequency*) secara internal, menerapkan saturasi melalui konstanta k₁ = 1,5, dan menormalisasi terhadap panjang dokumen melalui konstanta b = 0,75, untuk menghasilkan skor relevansi akhir (RSV).

Secara kualitatif, mekanisme ini dirancang agar produk dengan teks deskripsi sangat panjang namun hanya berisi pengulangan kata kunci (*keyword stuffing*) mengalami penalti skor akibat fungsi normalisasi panjang dokumen bawaan BM25, sementara deskripsi produk yang padat dan relevan terhadap kueri memperoleh skor RSV yang lebih tinggi. Produk yang melampaui ambang batas relevansi (*threshold*) 10% selanjutnya difilter berdasarkan kriteria pengguna (Bagian III.C, KF-3), lalu diurutkan untuk menghasilkan 15 rekomendasi teratas.

**[Contoh perhitungan BM25 langkah-demi-langkah menggunakan kueri dan dokumen nyata dari dataset — lihat placeholder pada Bagian III.D.2 — akan disisipkan di sini]**

## D. Hasil Evaluasi

Evaluasi dijalankan terhadap 14 kueri uji berlabel (Bagian III.F) pada 526 produk asli, dengan K=10. Angka berikut diambil langsung dari halaman **Evaluasi Resmi** aplikasi (`/evaluasi/paper/`), yang menyatakan eksplisit bahwa hasilnya dihitung live setiap kali halaman dimuat menggunakan logika yang sama persis dengan `python manage.py run_evaluation` — tidak ada angka yang di-cache atau dikarang.

TABLE II. HASIL EVALUASI BM25 vs TF-IDF (RATA-RATA 14 KUERI, K=10)

| Method | Precision@10 | Recall@10 | Hit Rate@10 | NDCG@10 | Avg. Query Time (ms) |
|---|---|---|---|---|---|
| TF-IDF + Cosine Similarity | 0.3214 | 0.5114 | 0.9286 | 0.4949 | 18.332 |
| Okapi BM25 (Proposed) | 0.6071 | 0.7925 | 1.0000 | 0.9229 | 10.922 |

Okapi BM25 unggul di seluruh metrik: Precision@10 hampir dua kali lipat TF-IDF (0,6071 vs 0,3214), Recall@10 lebih tinggi (0,7925 vs 0,5114), Hit Rate@10 sempurna 1,0000 (TF-IDF 0,9286 — berarti pada sebagian kueri TF-IDF tidak menemukan satu pun produk relevan di Top-10), NDCG@10 hampir dua kali lipat (0,9229 vs 0,4949), dan waktu komputasi rata-rata justru lebih cepat (10,92 ms vs 18,33 ms per kueri).

**[Rincian hasil per kueri (14 baris) tersedia di halaman `/evaluasi/paper/` dan dapat disisipkan sebagai tabel lampiran/Fig. jika dosen meminta rincian granular saat presentasi]**

## E. Perbandingan dengan TF-IDF + Cosine Similarity

Perbandingan metode ini bertujuan mengukur signifikansi kontribusi algoritma Okapi BM25 dibandingkan baseline TF-IDF + Cosine Similarity (Bagian III.D.1), dijalankan pada dataset, preprocessing, dan kueri uji yang identik (Bagian III.F) untuk memastikan validitas metodologis perbandingan.

Sebagai pemeriksaan tambahan terhadap keandalan hasil pada Tabel II (bukan pengganti, melainkan pelengkap — Tabel II tetap acuan resmi), tiga kueri bebas di luar 14 kueri kurasi resmi dijalankan melalui halaman perbandingan live aplikasi (`/evaluasi/`) untuk memastikan pola keunggulan BM25 tidak spesifik terhadap 14 kueri yang dikurasi:

TABLE III. SANITY CHECK — 3 KUERI DI LUAR SET RESMI (RATA-RATA 2 DARI 3 KUERI YANG TERDETEKSI ATRIBUT TERSTRUKTURNYA)

| Method | Precision@10 | Recall@10 | Hit Rate@10 | NDCG@10 |
|---|---|---|---|---|
| TF-IDF + Cosine Similarity | 0.9000 | 0.5132 | 1.0000 | 0.9132 |
| Okapi BM25 | 0.9500 | 0.5444 | 1.0000 | 0.9682 |

Pola yang sama (BM25 ≥ TF-IDF di setiap metrik) kembali terlihat. Kueri ketiga dari sanity check ini ("iphone second murah dibawah 3 juta") tidak memiliki atribut terstruktur yang dapat dideteksi (tidak menyebut varian/storage/platform/battery/wilayah spesifik), sehingga metriknya tidak terdefinisi (bukan nol) — namun ditemukan observasi menarik: TF-IDF + Cosine Similarity mengembalikan **0 hasil** untuk kueri ini, sementara BM25 tetap mengembalikan 10 hasil (dengan skor relevansi sangat rendah, 0,0014–0,0016). *[Penyebab pasti perbedaan ini — apakah TF-IDF memiliki ambang similarity minimum atau penanganan vektor kosong yang berbeda dari BM25 — perlu diverifikasi langsung di source code pada Tahap 3, bukan diasumsikan di sini.]*

## F. Diskusi

Hasil pada Tabel II dan III secara konsisten menunjukkan Okapi BM25 lebih unggul dibandingkan TF-IDF + Cosine Similarity pada seluruh metrik evaluasi standar information retrieval (Precision@10, Recall@10, Hit Rate@10, NDCG@10), sekaligus dengan waktu komputasi yang lebih rendah. Pola ini konsisten baik pada 14 kueri kurasi resmi maupun pada kueri bebas di luar set tersebut, sehingga tidak nampak sebagai artefak pemilihan kueri.

Kandidat penjelasan yang selaras dengan karakteristik BM25 (Bagian III.D.2) dan perlu diverifikasi lebih lanjut terhadap struktur dataset aktual: deskripsi produk pada dataset ini memiliki panjang yang bervariasi antar-penjual (disebutkan di Bab I sebagai sumber *keyword stuffing*), sehingga fungsi normalisasi panjang dokumen BM25 (parameter *b*) kemungkinan berperan signifikan dalam mencegah dokumen dengan deskripsi panjang namun repetitif memperoleh skor yang tidak proporsional — sesuatu yang tidak dimiliki TF-IDF murni. Selisih Hit Rate@10 (1,0000 vs 0,9286) juga mengindikasikan ada kueri di mana TF-IDF gagal total menemukan produk relevan di Top-10, sejalan dengan observasi kueri tanpa atribut terstruktur pada Bagian IV-E yang membuat TF-IDF mengembalikan nol hasil.

Kekuatan sistem: BM25 terbukti memberi hasil yang relevan (Precision@10 di atas 0,6) sekaligus responsif (rata-rata di bawah 11 ms per kueri), mendukung klaim sistem sebagai *decision support system* yang layak dipakai secara langsung oleh calon pembeli.

Keterbatasan: ground truth pada evaluasi ini bersifat deterministik berbasis kecocokan atribut terstruktur (Bagian III.F), sehingga belum menangkap relevansi semantik/kontekstual yang tidak eksplisit disebut dalam kueri (terlihat pada kueri "iphone second murah dibawah 3 juta" yang tidak dapat dievaluasi). Selisih jumlah produk 526 vs 527 (Bab IV-B) juga perlu dipastikan tidak memengaruhi validitas perbandingan sebelum angka ini difinalisasi ke paper yang dikumpulkan.

# V. KESIMPULAN

Penelitian ini bertujuan menyelesaikan masalah kecocokan informasi dan kesulitan calon konsumen dalam menyeleksi produk iPhone bekas di berbagai platform marketplace akibat tingginya variabilitas teks deskripsi penjual. Sebagai solusi, penelitian ini merancang dan mengimplementasikan sistem rekomendasi *iRecom Master* menggunakan algoritma *Information Retrieval* probabilistik Okapi BM25 sebagai metode utama, diperkuat dengan *hard filter* numerik untuk menyaring batasan harga dan tingkat kesehatan baterai (*battery health*), serta dibandingkan secara empiris terhadap baseline TF-IDF + Cosine Similarity.

Hasil evaluasi terhadap 14 kueri uji berlabel pada 526 produk asli membuktikan Okapi BM25 unggul di seluruh metrik dibandingkan baseline TF-IDF + Cosine Similarity: Precision@10 0,6071 vs 0,3214, Recall@10 0,7925 vs 0,5114, Hit Rate@10 1,0000 vs 0,9286, dan NDCG@10 0,9229 vs 0,4949 — sekaligus waktu komputasi rata-rata lebih rendah (10,92 ms vs 18,33 ms per kueri). Keunggulan ini juga terkonfirmasi pada kueri uji tambahan di luar set kurasi resmi (Tabel III), menunjukkan hasil tidak bergantung pada pemilihan kueri tertentu.

Kontribusi utama penelitian ini adalah terciptanya perangkat lunak pendukung keputusan (*decision support system*) yang objektif dan terukur untuk pasar iPhone bekas, sekaligus bukti empiris perbandingan BM25 dan TF-IDF + Cosine Similarity pada domain deskripsi produk marketplace berbahasa Indonesia yang tidak terstruktur — sesuatu yang belum banyak dikaji pada penelitian terdahulu (Bab II).

Penelitian ini masih memiliki keterbatasan. Variabel penilaian saat ini baru berfokus pada kesesuaian teks deskripsi dan spesifikasi kuantitatif dasar, sehingga sistem belum mampu memvalidasi kredibilitas riil dari pihak penjual, dan ground truth evaluasi masih bersifat deterministik berbasis kecocokan atribut terstruktur (bukan data interaksi pengguna riil), sehingga belum menangkap relevansi semantik/kontekstual yang tidak eksplisit disebutkan dalam kueri. Saran pengembangan (*future work*) meliputi penambahan fitur ekstraksi dan visibilitas nilai ulasan (*rating*) produk dari masing-masing toko sebagai acuan prioritas tambahan, penyajian komentar pembeli terbaik (*top-rated comments*) pada antarmuka detail produk, serta perluasan evaluasi menggunakan data interaksi pengguna riil di masa mendatang.

# Acknowledgment

*[Sesuaikan kalimat berikut dengan penggunaan AI generatif aktual oleh tim, sesuai kebijakan disclosure IEEE pada pedoman dosen bagian vi]*

Penulis menggunakan asisten AI untuk membantu audit konsistensi paper terhadap pedoman, penyuntingan bahasa ilmiah, dan penyusunan struktur Bab IV. Seluruh konten substantif, implementasi, hasil eksperimen, dan kesimpulan tetap ditinjau dan divalidasi sepenuhnya oleh penulis.

# References

[1] A. Rachmaniar, S. Widayati, and K. Rokoyah, "Sistem Rekomendasi Produk E-Commerce menggunakan Collaborative Filtering dan Content-Based Filtering," *Journal of Information System, Informatics and Computing*, vol. 9, no. 1, p. 40, May 2025, doi: 10.52362/jisicom.v9i1.1904.

[2] S. H. Alviyanti, A. Purwandira, I. Febiyanti, E. Daniati, and A. Ristyawan, "Klasifikasi Sentimen Pengguna Aplikasi Livin By Mandiri Pada Playstore Menggunakan Algoritma Naive Bayes," Online, 2024.

[3] M. Agustina, Y. Azhar, and N. Hayatin, "Sistem Perekomendasi Dosen Pembimbing berdasarkan Relevansi Topik Tugas Akhir menggunakan Metode Okapi BM25," *REPOSITOR*, vol. 2, no. 9, pp. 1203-1212, 2020.

[4] M. P. Simatupang and D. P. Utomo, "Analisa Testimonial dengan menggunakan Algoritma Text Mining dan Term Frequency-Inverse Document Frequency (TF-IDF) pada Toko Allmeeart," *KOMIK (Konferensi Nasional Teknologi Informasi dan Komputer)*, vol. 3, no. 1, Dec. 2019, doi: 10.30865/komik.v3i1.1697.

[5] I. Darmawan, M. Nazir Arifin, N. Ramadhani, and N. Puspa Dewi, "Algoritma Okapi BM25 dalam Sistem Pencarian Informasi berbasis Teks," *Jurnal Insand Comtech*, vol. 10, no. 1, 2025.

[6] Arya Mahendrata Diningrat, "Optimasi Algoritma Pencarian Dokumen Akademik Menggunakan BM25 dan TF-IDF," May 2025.

[7] R. Ridlo Baihaqi, "Temu Kembali Informasi pada Berita Olahraga Berbahasa Indonesia dengan Seleksi Fitur Term Frequency dan Metode BM25," 2020. [Online]. Available: http://j-ptiik.ub.ac.id

[8] I. Fernández-Tobías, I. Cantador, M. Kaminskas, and F. Ricci, "Cross-domain recommender systems: A survey of the State of the Art."

[9] Y. Fadhila Hernawan, P. P. Adikara, R. C. Wihandika, and P. Korespondensi, "Peringkasan Artikel Berbahasa Indonesia menggunakan TextRank dengan Pembobotan BM25," vol. 9, no. 1, pp. 61-68, 2022, doi: 10.25126/jtiik.202293765.

[10] M. A. Hanan, M. Haikal, A. Kamily, R. Hakim, T. A. Priambodo, and J. E. Manggoa, "Analisis Pengaruh Review dan Star Rating terhadap Jual Beli Smartphone di E-Commerce Flipkart."

[11] A. Agustian, A. I. Hadiana, and A. B. A. Rahman, "Perbandingan TF-IDF dengan Count Vectorization Dalam Content-Based Filtering Rekomendasi Mobil Listrik," *Explore IT: Jurnal Keilmuan dan Aplikasi Teknik Informatika*, 2023. *[Referensi baru — ditemukan dan diverifikasi via pencarian web selama revisi ini; mohon tim mengecek ulang volume/nomor/halaman persis dari sumber asli untuk melengkapi sitasi]*

*[Referensi [12]–[15] untuk baris Tabel I nomor 6, 7, 8, 11, 13, 14, 15 (ditandai [†]) masih dibutuhkan — lihat catatan poin 12 di atas. Total referensi saat ini: 11 dari minimal 12–15 yang disyaratkan pedoman.]*
