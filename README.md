# SIREKMA: Sistem Rekomendasi Kost Mahasiswa

**SIREKMA (Sistem Rekomendasi Kost Mahasiswa)** merupakan sistem rekomendasi berbasis Python dengan antarmuka interaktif menggunakan **Streamlit** yang dirancang untuk membantu mahasiswa dalam memilih kost terbaik sesuai kebutuhan dan preferensi mereka. Sistem ini menggunakan metode **MOORA (Multi-Objective Optimization on the basis of Ratio Analysis)** untuk menilai dan memberikan peringkat rekomendasi kost secara objektif dan transparan.

Dataset yang digunakan dalam SIREKMA berisi beberapa variabel penting yang menjadi faktor pertimbangan utama dalam memilih tempat kost, yaitu:

| **Kriteria**     | **Satuan** | **Deskripsi** |
|------------------|------------|----------------|
| Name             | String     | Nama atau identitas kost. |
| Price            | IDR        | Harga sewa kost per bulan. |
| Distance         | km         | Jarak kost dari kampus atau lokasi tujuan utama mahasiswa. |
| Size             | m²         | Ukuran atau luas kamar kost. |
| WiFi             | Mbps       | Ketersediaan fasilitas internet WiFi. |
| Security Score   | 0–10       | Skor keamanan lingkungan kost. |

Melalui proses perhitungan berbasis algoritma pemeringkatan (ranking) dengan menggunakan MOORA, SIREKMA menghasilkan daftar rekomendasi kost terbaik dengan urutan prioritas berdasarkan kombinasi variabel tersebut. Hasil rekomendasi ditampilkan secara real-time dalam antarmuka Streamlit yang sederhana dan mudah dipahami. Selain itu, sistem menyediakan fitur unduh hasil rekomendasi dalam format .CSV, sehingga pengguna dapat menyimpan dan menganalisis data secara mandiri di luar aplikasi.

Dengan SIREKMA, mahasiswa dapat mengambil keputusan lebih cepat, akurat, dan efisien dalam memilih kost yang paling sesuai dengan kebutuhan, preferensi, serta kondisi finansial mereka.

## Installation
Clone repository dengan menjalankan perintah berikut:

```shell
git clone https://github.com/Superior231/sirekma.git
```

Pastikan Anda telah membuat Virtual Environment sebelumnya. Jalankan perintah berikut untuk membuat Virtual Environment:

```shell
python -m venv venv
venv\Scripts\activate
```

Setelah membuat Virtual Environment, Anda dapat menginstal library yang diperlukan dengan menjalankan perintah berikut:

```shell
pip install -r requirements.txt
```

## Usage
Jalankan perintah berikut untuk memulai server:

```shell
streamlit run app.py
```

Server akan dijalankan di port 8501. Buka url `http://localhost:8501/` di browser Anda untuk mengakses SIREKMA.
