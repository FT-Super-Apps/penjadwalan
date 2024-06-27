Berikut adalah contoh file `README.md` dalam bahasa Indonesia yang menjelaskan proyek Anda:

```markdown
# Penjadwalan Kuliah Menggunakan Algoritma Genetika

Proyek ini bertujuan untuk membuat penjadwalan kuliah yang optimal menggunakan algoritma genetika. Sistem ini mempertimbangkan preferensi waktu dosen, menghindari bentrok waktu, dan memastikan distribusi ruangan yang efisien.

## Struktur Data

### 1. Data Kuliah (`kuliah_teknik`)
Menyimpan informasi mengenai mata kuliah, termasuk kode mata kuliah, nama mata kuliah, dosen pengajar, dan jumlah SKS.

Contoh:
```python
dataKuliah = [
    {'id': 1, 'kode': 'KT001', 'nama': 'Matematika', 'dosen': 'Dr. A', 'sks': 3},
    {'id': 2, 'kode': 'KT002', 'nama': 'Fisika', 'dosen': 'Dr. B', 'sks': 2},
    {'id': 3, 'kode': 'KT003', 'nama': 'Kimia', 'dosen': 'Dr. C', 'sks': 2},
    {'id': 4, 'kode': 'KT004', 'nama': 'Biologi', 'dosen': 'Dr. D', 'sks': 3}
]
```

### 2. Data Waktu (`waktu2`)
Menyimpan informasi mengenai waktu perkuliahan.

Contoh:
```python
dataWaktu = [
    {'id': 1, 'hari': 'Senin', 'jam_mulai': '08:00', 'jam_selesai': '10:00'},
    {'id': 2, 'hari': 'Senin', 'jam_mulai': '10:00', 'jam_selesai': '12:00'},
    {'id': 3, 'hari': 'Selasa', 'jam_mulai': '08:00', 'jam_selesai': '10:00'},
    {'id': 4, 'hari': 'Selasa', 'jam_mulai': '10:00', 'jam_selesai': '12:00'}
]
```

### 3. Data Ruangan (`ruangan`)
Menyimpan informasi mengenai ruangan perkuliahan.

Contoh:
```python
dataRuangan = [
    {'id': 1, 'nama': 'Ruang 101'},
    {'id': 2, 'nama': 'Ruang 102'},
    {'id': 3, 'nama': 'Ruang 103'},
    {'id': 4, 'nama': 'Ruang 104'}
]
```

### 4. Preferensi Waktu Dosen (`preferensi_waktu_dosen`)
Menyimpan informasi mengenai preferensi waktu dosen untuk mengajar.

Contoh:
```python
dataPreferensiDosen = [
    {'dosen': 'Dr. A', 'preferensi_waktu': [1, 2]},  # Dr. A prefers to teach at time slots 1 and 2
    {'dosen': 'Dr. B', 'preferensi_waktu': [3, 4]},  # Dr. B prefers to teach at time slots 3 and 4
    {'dosen': 'Dr. C', 'preferensi_waktu': [1, 3]},  # Dr. C prefers to teach at time slots 1 and 3
    {'dosen': 'Dr. D', 'preferensi_waktu': [2, 4]}   # Dr. D prefers to teach at time slots 2 and 4
]
```

## Penggunaan

### Menghasilkan Data
Fungsi `GenerateData` mengubah daftar kamus menjadi format yang sesuai untuk digunakan dalam algoritma.

Contoh:
```python
def GenerateData(data):
    return data

kuliah = GenerateData(dataKuliah)
waktu = GenerateData(dataWaktu)
ruangan = GenerateData(dataRuangan)
preferensi_dosen = {item['dosen']: item['preferensi_waktu'] for item in dataPreferensiDosen}
```

### Menjalankan Algoritma
Kode utama untuk menjalankan algoritma genetika adalah sebagai berikut:

```python
# Inisialisasi data
start_time = perf_counter()
generateCromosom()
while generataion < max_generataion and not success:
    generataion += 1
    print(f"\nGenerasi ke-{generataion}")
    calculate_all_fitness()
    showFitness()
    if not success:
        getCromosomProbability()
        seleksi()
    if not success:
        crossover()
    if not success:
        mutation()
end_time = perf_counter()

print("\nCROMOSSOM TERBAIK:")
clash = {**fitness[best_cromosom]['clash']['cr'], **fitness[best_cromosom]['clash']['cd']}
arr = []

for i, val in enumerate(crommosom[best_cromosom]):
    newval = list(val.values())
    values = ' , '.join(str(v) for v in newval)
    if i in clash:
        arr.append(f"Danger : [{values}]")
    else:
        arr.append(f"[{values}]")

arrjoin = ' , '.join(arr)
print(f"Individu[{best_cromosom}]: ( {arrjoin} )")
print('\n\nRAM usage is {} MB(Megabytes)'.format(int(get_ram_usage() / 1024 / 1024)))
print('Elapsed wall clock time = %g seconds.' % (end_time - start_time))
```

## Lisensi
Proyek ini dilisensikan di bawah lisensi MIT. Lihat file `LICENSE` untuk informasi lebih lanjut.
```

Pastikan untuk menyesuaikan nama tabel dan format data pada database Anda agar sesuai dengan skema yang digunakan dalam kode ini. Anda juga bisa menambahkan lebih banyak detail pada README sesuai kebutuhan proyek Anda.
