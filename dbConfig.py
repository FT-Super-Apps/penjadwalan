# Mock database configuration for testing enhanced scheduling system

def GetAllDB(table_name):
    """Mock function to simulate database queries"""
    
    if table_name == 'kuliah_teknik':
        return [
            {'id': 0, 'nama': 'Algoritma & Pemrograman', 'dosen': 'Dr. Ahmad', 'sks': 3},
            {'id': 1, 'nama': 'Basis Data', 'dosen': 'Dr. Budi', 'sks': 3},
            {'id': 2, 'nama': 'Jaringan Komputer', 'dosen': 'Dr. Ahmad', 'sks': 2},
            {'id': 3, 'nama': 'Sistem Operasi', 'dosen': 'Dr. Citra', 'sks': 3},
            {'id': 4, 'nama': 'Pemrograman Web', 'dosen': 'Dr. Budi', 'sks': 2},
        ]
    
    elif table_name == 'waktu2':
        return [
            {'id': 0, 'hari': 'Senin', 'jam_mulai': '08:00'},
            {'id': 1, 'hari': 'Senin', 'jam_mulai': '10:00'},
            {'id': 2, 'hari': 'Selasa', 'jam_mulai': '08:00'},
            {'id': 3, 'hari': 'Selasa', 'jam_mulai': '10:00'},
            {'id': 4, 'hari': 'Rabu', 'jam_mulai': '08:00'},
            {'id': 5, 'hari': 'Rabu', 'jam_mulai': '10:00'},
            {'id': 6, 'hari': 'Kamis', 'jam_mulai': '08:00'},
            {'id': 7, 'hari': 'Kamis', 'jam_mulai': '10:00'},
            {'id': 8, 'hari': 'Jumat', 'jam_mulai': '08:00'},
        ]
    
    elif table_name == 'ruangan':
        return [
            {'id': 0, 'nama': 'Lab Komputer 1', 'kapasitas': 30},
            {'id': 1, 'nama': 'Lab Komputer 2', 'kapasitas': 25},
            {'id': 2, 'nama': 'Ruang Kelas A', 'kapasitas': 40},
            {'id': 3, 'nama': 'Ruang Kelas B', 'kapasitas': 35},
        ]
    
    elif table_name == 'preferensi_waktu_dosen':
        return [
            {'dosen': 'Dr. Ahmad', 'preferensi_waktu': [0, 2, 4], 'tidak_bisa_waktu': [8]},
            {'dosen': 'Dr. Budi', 'preferensi_waktu': [1, 3, 5], 'tidak_bisa_waktu': [0]},
            {'dosen': 'Dr. Citra', 'preferensi_waktu': [6, 7], 'tidak_bisa_waktu': [1, 8]},
        ]
    
    return []

def GenerateData(raw_data):
    """Convert raw database data to format expected by the scheduling algorithm"""
    result = []
    
    for item in raw_data:
        if 'hari' in item and 'jam_mulai' in item:
            # For waktu data: [id, hari, jam_mulai]
            result.append([item['id'], item['hari'], item['jam_mulai']])
        elif 'nama' in item and 'kapasitas' in item:
            # For ruangan data: [id, nama, kapasitas]
            result.append([item['id'], item['nama'], item['kapasitas']])
        elif 'nama' in item and 'dosen' in item and 'sks' in item:
            # For kuliah data: keep as dict for easier access
            result.append(item)
    
    return result