# Proyek Capstone: Pipeline Big Data E-Commerce

[cite_start]Dokumentasi ini merangkum langkah-langkah teknis yang diambil untuk membangun *end-to-end data pipeline* sederhana, sesuai dengan tugas "Big Data Capstone Project"[cite: 1]. [cite_start]Pipeline ini mencakup proses Ingestion, Storage, Processing, dan Visualization data penjualan e-commerce[cite: 5, 41].

## 1. Arsitektur Sistem

Arsitektur yang diimplementasikan menggunakan alat-alat berikut:

* **Environment:** Windows Subsystem for Linux (WSL) - Ubuntu
* **Containerization:** Docker Desktop & Docker Compose
* **Ingestion:** Docker CLI (`docker cp`), HDFS CLI (`hdfs dfs -put`)
* **Storage:** Hadoop (HDFS) (Berjalan di container `namenode` & `datanode`)
* **Processing:** Apache Spark (PySpark) (Berjalan di container `spark-master` & `spark-worker`)
* **Visualization:** Python 3 (Pandas, Matplotlib) (Berjalan di Ubuntu/WSL lokal)

## 2. Langkah-langkah Eksekusi

Berikut adalah catatan eksekusi perintah yang berhasil dilakukan dari awal hingga akhir.

### Tahap 0: Persiapan dan Menjalankan Layanan

1.  **Masuk ke Direktori Proyek**
    Semua perintah dijalankan dari direktori yang berisi `docker-compose.yml`.
    ```bash
    cd ~/bigdata-project
    ```

2.  **Menjalankan Container**
    Memulai semua layanan HDFS dan Spark di *background*.
    ```bash
    docker-compose up -d
    ```

### Tahap 1: Ingestion (Data ke HDFS)

Tujuan: Memindahkan file `ecommerce.parquet` dari *filesystem* Windows ke *filesystem* HDFS di dalam Docker.

1.  **Salin File dari Windows ke Container**
    Menyalin file dari folder `Downloads` Windows (diakses melalui `/mnt/c/` di WSL) ke folder `/tmp` di dalam container `namenode`.
    ```bash
    docker cp /mnt/c/Users/juank/Downloads/ecommerce.parquet namenode:/tmp/ecommerce.parquet
    ```

2.  **Buat Direktori di HDFS**
    Membuat folder `/proyek_bigdata` di *dalam* HDFS untuk menyimpan file proyek.
    ```bash
    docker exec namenode hdfs dfs -mkdir -p /proyek_bigdata
    ```

3.  **Masukkan File ke HDFS**
    Memindahkan file dari *filesystem* container (`/tmp`) ke *filesystem* HDFS (`/proyek_bigdata/`).
    ```bash
    docker exec namenode hdfs dfs -put /tmp/ecommerce.parquet /proyek_bigdata/
    ```
    [cite_start]**Hasil:** File data mentah berhasil disimpan di HDFS dan siap diproses[cite: 14].

### Tahap 2: Processing (Spark SQL/PySpark)

[cite_start]Tujuan: Menjalankan skrip PySpark (`proses.py`) untuk membaca data dari HDFS, melakukan agregasi [cite: 20][cite_start], dan menyimpan hasilnya kembali ke HDFS[cite: 21].

1.  **Salin Skrip PySpark ke Container Spark**
    Menyalin skrip `proses.py` dari direktori *home* Ubuntu (`../`) ke folder `/tmp` di dalam container `spark-master`.
    ```bash
    # Dijalankan dari ~/bigdata-project
    docker cp ../proses.py spark-master:/tmp/proses.py
    ```

2.  **Jalankan Job Spark**
    Mengeksekusi skrip PySpark menggunakan `spark-submit`. Path lengkap `/spark/bin/spark-submit` digunakan karena *executable*-nya tidak ada di `PATH` default.
    ```bash
    docker exec spark-master /spark/bin/spark-submit /tmp/proses.py
    ```
    [cite_start]**Hasil:** Skrip berhasil dieksekusi, membaca data dari `hdfs://namenode:9000`, melakukan agregasi, dan menyimpan hasilnya ke `hdfs://namenode:9000/proyek_bigdata/hasil_agregasi`[cite: 14].

### Tahap 3: Visualization (Python Lokal)

[cite_start]Tujuan: Mengambil data hasil agregasi dari HDFS, membawanya ke mesin lokal (Ubuntu), dan membuat visualisasi[cite: 22].

1.  **Ambil Hasil Agregasi dari HDFS**
    Menyalin data hasil (`hasil_agregasi`) dari HDFS ke *filesystem* sementara (`/tmp`) di container `namenode`.
    ```bash
    docker exec namenode hdfs dfs -get /proyek_bigdata/hasil_agregasi /tmp/
    ```

2.  **Salin Hasil ke Lokal (Ubuntu)**
    Menyalin folder `hasil_agregasi` dari container `namenode` ke direktori `bigdata-project` di Ubuntu. Tanda `.` merujuk pada direktori saat ini.
    ```bash
    docker cp namenode:/tmp/hasil_agregasi .
    ```

3.  **Instalasi Library Python**
    Menginstal `pip` dan *library* yang diperlukan (Pandas, Matplotlib, PyArrow) di Ubuntu untuk skrip visualisasi.
    ```bash
    sudo apt update
    sudo apt install python3-pip
    pip install pandas matplotlib pyarrow
    ```

4.  **Jalankan Skrip Visualisasi**
    Mengeksekusi skrip `visualisasi.py` di terminal Ubuntu. Skrip ini membaca data dari folder `hasil_agregasi` lokal dan menghasilkan grafik.
    ```bash
    python3 visualisasi.py
    ```
    **Hasil:** File `penjualan_bulanan.png` berhasil dibuat di direktori `bigdata-project`.

### Tahap 4: Mengakses Hasil Akhir

Untuk melihat file `penjualan_bulanan.png` di Windows, file tersebut disalin ke folder `Downloads` Windows.

```bash
cp penjualan_bulanan.png /mnt/c/Users/juank/Downloads/
