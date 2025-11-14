from pyspark.sql import SparkSession
from pyspark.sql.functions import to_timestamp, month, sum, col, year

# 1. Inisialisasi SparkSession
spark = SparkSession.builder \
    .appName("Proses Agregasi E-Commerce") \
    .getOrCreate()

print("--- Sesi Spark berhasil dibuat. ---")

try:
    # 2. Baca file Parquet DARI HDFS
    #    (Ganti localhost:9000 jika HDFS Anda berjalan di port berbeda)
    input_path = "hdfs://namenode:9000/proyek_bigdata/ecommerce.parquet"
    df = spark.read.parquet(input_path)
    
    print(f"--- Berhasil membaca data dari {input_path} ---")
    df.printSchema() # Tampilkan skema untuk debugging

    # 3. Transformasi & Agregasi
    #    Tujuan: Agregasi penjualan per bulan/kategori [cite: 20]
    
    # 3a. Ubah 'InvoiceDate' (string) menjadi format timestamp
    #     Format 'M/d/yyyy H:mm' adalah asumsi umum untuk dataset E-commerce Kaggle
    df_with_date = df.withColumn("TanggalInvoice", 
                                 to_timestamp(col("InvoiceDate"), "M/d/yyyy H:mm"))

    # 3b. Ekstrak 'Bulan' dan 'Tahun'
    df_with_month_year = df_with_date.withColumn("Bulan", month(col("TanggalInvoice"))) \
                                     .withColumn("Tahun", year(col("TanggalInvoice")))

    # 3c. Lakukan agregasi (Group By)
    print("--- Melakukan agregasi penjualan... ---")
    # Asumsi agregasi berdasarkan 'StockCode' (lebih unik dari 'Description') dan 'Bulan'
    agregasi_penjualan = df_with_month_year.groupBy("Tahun", "Bulan", "StockCode") \
        .agg(sum("Quantity").alias("TotalTerjual")) \
        .orderBy(col("Tahun").asc(), col("Bulan").asc(), col("TotalTerjual").desc())

    # 4. Tampilkan hasil agregasi (Output Minggu 2) 
    print("--- Hasil Agregasi (Top 20) ---")
    agregasi_penjualan.show()

    # 5. Simpan hasil akhir ke Parquet di HDFS (Deliverable) [cite: 21]
    output_path = "hdfs://namenode:9000/proyek_bigdata/hasil_agregasi"
    agregasi_penjualan.write.mode("overwrite").parquet(output_path)
    
    print(f"--- Hasil agregasi berhasil disimpan ke {output_path} ---")

except Exception as e:
    print(f"Terjadi error: {e}")

finally:
    # 6. Hentikan sesi Spark
    spark.stop()
    print("--- Sesi Spark ditutup. ---")
