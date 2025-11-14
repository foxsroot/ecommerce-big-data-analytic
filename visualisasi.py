import pandas as pd
import matplotlib.pyplot as plt
import glob # Untuk mencari file parquet secara otomatis
import os

print("--- Memulai skrip visualisasi... ---")

try:
    # Tentukan path folder
    folder_path = 'hasil_agregasi'
    
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' tidak ditemukan.")
        print("Pastikan Anda sudah menjalankan 'docker cp' dari langkah sebelumnya.")
    else:
        # Cari semua file Parquet di dalam folder hasil_agregasi
        parquet_files = glob.glob(os.path.join(folder_path, "part-*.parquet"))
        
        if not parquet_files:
            print(f"Error: Tidak ditemukan file 'part-*.parquet' di dalam folder '{folder_path}'.")
        else:
            print(f"Membaca file: {parquet_files[0]}")
            # Baca file parquet (kita hanya ambil yang pertama jika ada banyak)
            df = pd.read_parquet(parquet_files[0])
            
            # PENTING: Bersihkan data null yang kita temukan di log Spark
            df_cleaned = df.dropna(subset=['Tahun', 'Bulan'])
            print(f"Data awal: {len(df)} baris, Data setelah dibersihkan: {len(df_cleaned)} baris.")

            # 2. Siapkan data untuk Insight (Tren Penjualan Bulanan Total)
            
            # Ubah Tahun dan Bulan menjadi integer agar bisa diurutkan
            df_cleaned['Tahun'] = df_cleaned['Tahun'].astype(int)
            df_cleaned['Bulan'] = df_cleaned['Bulan'].astype(int)
            
            # Urutkan berdasarkan Tahun dan Bulan
            df_sorted = df_cleaned.sort_values(by=["Tahun", "Bulan"])
            
            # Buat kolom 'TahunBulan' untuk label sumbu X
            df_sorted['TahunBulan'] = df_sorted['Tahun'].astype(str) + '-' + df_sorted['Bulan'].astype(str).str.zfill(2)
            
            # Agregasi total penjualan per TahunBulan
            penjualan_bulanan = df_sorted.groupby('TahunBulan')['TotalTerjual'].sum()

            # 3. Buat Grafik (Deliverable Minggu 3)
            print("--- Membuat grafik 'penjualan_bulanan.png'... ---")
            plt.figure(figsize=(12, 6))
            penjualan_bulanan.plot(kind='line', marker='o', color='blue')
            
            plt.title('Tren Total Penjualan Bulanan (Agregasi dari Spark)')
            plt.xlabel('Tahun-Bulan')
            plt.ylabel('Total Kuantitas Terjual')
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Simpan grafik sebagai file gambar
            plt.savefig('penjualan_bulanan.png')

            print("--- Grafik berhasil disimpan! ---")
            print("File 'penjualan_bulanan.png' siap digunakan untuk laporan Anda.")

except Exception as e:
    print(f"Terjadi error: {e}")
