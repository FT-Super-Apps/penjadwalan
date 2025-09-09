# Enhanced University Course Scheduling System

🎓 **Sistem Penjadwalan Kuliah Berbasis Algoritma Genetika dengan Fitur Enhanced Preferences**

Sistem penjadwalan otomatis untuk perguruan tinggi yang mendukung **exclusive time slots**, preferensi dosen berlevel, dan optimasi constraint yang intelligent.

## ✨ Fitur Utama

### 🔒 **Reserved Slots System**
- **Exclusive Time Slots**: Dosen senior dapat memesan slot waktu khusus
- **Pre-allocation**: Sistem melindungi reserved slots sebelum optimasi dimulai
- **Conflict Detection**: Validasi otomatis untuk mencegah double booking
- **Priority Management**: Hierarki akses berdasarkan senioritas atau jabatan

### 📊 **Enhanced Preference System**
- **3 Level Preferensi**:
  - `reserved_slots`: Waktu eksklusif (penalty tertinggi jika dilanggar)
  - `preferred_slots`: Waktu yang disukai dosen
  - `blocked_slots`: Waktu yang tidak bisa digunakan

### 🎯 **Intelligent Genetic Algorithm**
- **Smart Mutation**: Mutasi berbasis preferensi dan constraint violations
- **Weighted Penalties**: Penalty berbeda untuk setiap jenis violation
- **Enhanced Fitness Function**: Optimasi multi-objective
- **Early Termination**: Berhenti otomatis jika solusi berkualitas tinggi ditemukan

### 📈 **Advanced Analytics**
- **Constraint Analysis**: Detail violations dengan kategori
- **Performance Metrics**: RAM usage dan execution time
- **Schedule Optimization Suggestions**: Rekomendasi slot terbaik untuk setiap dosen
- **Visual Status Indicators**: Color coding untuk berbagai status

## 🛠 Instalasi

### Prerequisites
```bash
pip install psutil colorama
```

### Setup Database
1. Import struktur database (lihat bagian Database Structure)
2. Sesuaikan konfigurasi di `dbConfig.py`
3. Atur enhanced preferences di kode utama

## 🚀 Usage

### Basic Usage
```bash
python jadwal-non-paralel.py
```

### Advanced Configuration
Edit preferensi dosen di file utama:

```python
preferensi_dosen_enhanced = {
    'Dr. Ahmad': {
        'reserved_slots': [{'waktu': 1, 'ruang': 0, 'priority': 'exclusive', 'reason': 'Research meeting'}],
        'preferred_slots': [{'waktu': 2}, {'waktu': 3}],
        'blocked_slots': [{'waktu': 8, 'reason': 'Administrative duty'}]
    }
}
```

## 📊 Database Structure

Sistem ini mendukung 4 tabel utama:

### 1. Tabel `kuliah_teknik`
```sql
CREATE TABLE kuliah_teknik (
    id INT PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    dosen VARCHAR(50) NOT NULL,
    sks INT NOT NULL
);

-- Contoh data
INSERT INTO kuliah_teknik VALUES 
(0, 'Algoritma & Pemrograman', 'Dr. Ahmad', 3),
(1, 'Basis Data', 'Dr. Budi', 3),
(2, 'Jaringan Komputer', 'Dr. Ahmad', 2),
(3, 'Sistem Operasi', 'Dr. Citra', 3),
(4, 'Pemrograman Web', 'Dr. Budi', 2);
```

### 2. Tabel `waktu2`
```sql
CREATE TABLE waktu2 (
    id INT PRIMARY KEY,
    hari VARCHAR(20) NOT NULL,
    jam_mulai TIME NOT NULL
);

-- Contoh data
INSERT INTO waktu2 VALUES 
(0, 'Senin', '08:00'),
(1, 'Senin', '10:00'),
(2, 'Selasa', '08:00'),
(3, 'Selasa', '10:00'),
(4, 'Rabu', '08:00'),
(5, 'Rabu', '10:00'),
(6, 'Kamis', '08:00'),
(7, 'Kamis', '10:00'),
(8, 'Jumat', '08:00');
```

### 3. Tabel `ruangan`
```sql
CREATE TABLE ruangan (
    id INT PRIMARY KEY,
    nama VARCHAR(50) NOT NULL,
    kapasitas INT NOT NULL
);

-- Contoh data
INSERT INTO ruangan VALUES 
(0, 'Lab Komputer 1', 30),
(1, 'Lab Komputer 2', 25),
(2, 'Ruang Kelas A', 40),
(3, 'Ruang Kelas B', 35);
```

### 4. Tabel `preferensi_waktu_dosen`
```sql
CREATE TABLE preferensi_waktu_dosen (
    dosen VARCHAR(50) PRIMARY KEY,
    preferensi_waktu TEXT, -- JSON array: [0,2,4]
    tidak_bisa_waktu TEXT  -- JSON array: [8]
);

-- Contoh data
INSERT INTO preferensi_waktu_dosen VALUES 
('Dr. Ahmad', '[0,2,4]', '[8]'),
('Dr. Budi', '[1,3,5]', '[0]'),
('Dr. Citra', '[6,7]', '[1,8]');
```

## 🔧 Konfigurasi Enhanced Preferences

### Format Konfigurasi

```python
preferensi_dosen_enhanced = {
    'NAMA_DOSEN': {
        'reserved_slots': [
            {
                'waktu': int,           # Index waktu (0-8)
                'ruang': int,           # Index ruang (0-3), optional
                'priority': 'exclusive', # Selalu 'exclusive'
                'reason': str           # Alasan reservasi
            }
        ],
        'preferred_slots': [
            {
                'waktu': int           # Index waktu yang disukai
            }
        ],
        'blocked_slots': [
            {
                'waktu': int,           # Index waktu yang diblok
                'reason': str           # Alasan blocking
            }
        ],
    }
}
```

### Contoh Lengkap

```python
preferensi_dosen_enhanced = {
    # Dosen Senior - Profesor dengan banyak privilege
    'Prof. Dr. Wiranto': {
        'reserved_slots': [
            {'waktu': 1, 'ruang': 0, 'priority': 'exclusive', 'reason': 'Weekly research meeting'},
            {'waktu': 5, 'priority': 'exclusive', 'reason': 'Senate meeting'}
        ],
        'preferred_slots': [
            {'waktu': 2},
            {'waktu': 4}
        ],
        'blocked_slots': [
            {'waktu': 8, 'reason': 'Jumatan'},
            {'waktu': 7, 'reason': 'Hospital duty'}
        ],
    },
    
    # Dosen Muda - Preferensi lebih fleksibel
    'Dr. Lisa Sari': {
        'reserved_slots': [],  # Tidak ada slot khusus
        'preferred_slots': [
            {'waktu': 0},   # Senin pagi
            {'waktu': 2}    # Selasa pagi
        ],
        'blocked_slots': [
            {'waktu': 8, 'reason': 'Jumatan'}
        ],
    },
    
    # Dosen Part-Time - Jadwal terbatas
    'Dr. Bambang Praktek': {
        'reserved_slots': [
            {'waktu': 1, 'priority': 'exclusive', 'reason': 'Clinic practice'}
        ],
        'preferred_slots': [
            {'waktu': 0},
            {'waktu': 2}
        ],
        'blocked_slots': [
            {'waktu': 3, 'reason': 'Clinic duty'},
            {'waktu': 4, 'reason': 'Clinic duty'},
            {'waktu': 5, 'reason': 'Clinic duty'},
            {'waktu': 6, 'reason': 'Clinic duty'},
            {'waktu': 7, 'reason': 'Clinic duty'},
            {'waktu': 8, 'reason': 'Jumatan'}
        ],
    }
}
```

## 📈 Weight Penalties

```python
preference_weights = {
    'exclusive': 1000,  # Reserved slots - TIDAK BOLEH DILANGGAR
    'preferred': 30,    # Preferensi waktu yang disukai
    'blocked': 50       # Waktu yang diblokir/tidak bisa
}
```

## 🎯 Algorithm Parameters

```python
# Genetic Algorithm Settings
jml_kromosom = 4        # Ukuran populasi
max_generataion = 10    # Maksimal generasi
crossover_rate = 75     # Tingkat crossover (%)
mutation_rate = 25      # Tingkat mutasi (%)
per_sks = 50           # 1 SKS = 50 menit

# Success Criteria
# Fitness = 1.0 jika tidak ada violations
# Early termination jika fitness > 0.95
```

## 📊 Output Analysis

### Sample Output
```
=== CONSTRAINT ANALYSIS ===
Reserved Slot Violations: 0
Preference Violations: 3
Traditional Clashes: 0
Total Penalties: 30

=== RESERVED SLOTS STATUS ===
✅ RESPECTED: Dr. Ahmad - waktu_1_ruang_0 (Research meeting)
✅ RESPECTED: Dr. Budi - waktu_5_ruang_1 (Senior faculty privilege)

=== SYSTEM PERFORMANCE ===
RAM usage: 3971 MB
Execution time: 0.123 seconds
Generations completed: 5
Success achieved: Yes
```

### Status Indicators
- ✅ **OK**: Tidak ada violation
- ⚠️ **CLASH**: Konflik waktu/ruangan
- 🔒 **RESERVED VIOLATION**: Melanggar slot eksklusif
- 📋 **PREFERENCE ISSUE**: Melanggar preferensi dosen

## 🔄 Workflow

1. **Initialization**: Pre-allocate reserved slots
2. **Validation**: Check conflicts dalam reserved slots
3. **Population Generation**: Generate kromosom awal
4. **GA Loop**:
   - Calculate enhanced fitness
   - Selection (Roulette Wheel)
   - Crossover dengan perbaikan
   - Intelligent mutation
5. **Results**: Analisis komprehensif dan recommendations

## 🎛 Customization

### Mengubah Priority Weights
```python
preference_weights = {
    'exclusive': 2000,  # Naikkan penalty reserved slots
    'preferred': 45,    # Naikkan penalty preferensi
    'blocked': 75       # Naikkan penalty blocked slots
}
```

### Mengubah Success Criteria
```python
# Di function calculate_fitness, ubah kondisi success
if len(reserved_violations) == 0 and total_penalties < 50:
    success = True
```

### Menambah Constraint Baru
```python
def check_custom_constraint(kromosom_data):
    violations = []
    # Implementasi constraint kustom
    return violations
```

## 🚨 Troubleshooting

### Error: "Reserved slot conflicts"
- Periksa konfigurasi `preferensi_dosen_enhanced`
- Pastikan tidak ada 2 dosen yang reserve slot sama

### Error: "No available slots"
- Kurangi jumlah reserved slots
- Tambahkan flexible slots untuk dosen
- Tingkatkan jumlah waktu/ruangan available

### Fitness rendah terus
- Turunkan penalty weights
- Tambahkan flexible slots
- Kurangi blocked slots

## 👥 Contributing

1. Fork repository
2. Buat feature branch
3. Commit changes dengan clear message
4. Push dan create Pull Request

## 📄 License

MIT License - feel free to use for academic and commercial purposes.

## 📞 Support

Untuk bantuan implementasi atau customization lebih lanjut, silakan buka issue di repository ini.

---

**Happy Scheduling! 🎓✨**