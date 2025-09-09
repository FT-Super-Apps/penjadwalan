# ===================================================================
# ENHANCED PREFERENCES CONFIGURATION EXAMPLES
# ===================================================================
# Contoh konfigurasi lengkap untuk sistem preferensi dosen enhanced
# File ini menunjukkan berbagai skenario penggunaan reserved slots dan preferensi

"""
Enhanced Preferences System mendukung 4 jenis konfigurasi:

1. RESERVED SLOTS - Waktu eksklusif yang WAJIB dihormati (penalty tertinggi)
2. PREFERRED SLOTS - Waktu yang disukai dengan tingkat prioritas
3. BLOCKED SLOTS - Waktu yang tidak bisa digunakan sama sekali
4. FLEXIBLE SLOTS - Waktu alternatif dengan prioritas rendah-sedang

Weight Penalties:
- exclusive: 1000 (reserved slots)
- high: 50
- medium: 30
- low: 10
"""

# ===================================================================
# SCENARIO 1: PROFESOR SENIOR DENGAN PRIVILEGE TINGGI
# ===================================================================

profesor_senior_config = {
    'Prof. Dr. Wiranto Hendro': {
        'reserved_slots': [
            {
                'waktu': 1,                    # Senin 10:00-11:40
                'ruang': 0,                    # Lab Komputer 1 (exclusive)
                'priority': 'exclusive',
                'reason': 'Weekly PhD supervision meeting'
            },
            {
                'waktu': 5,                    # Rabu 10:00-11:40  
                'priority': 'exclusive',       # Any room (ruang tidak dispesifikasi)
                'reason': 'Senate meeting - requires flexible room'
            },
            {
                'waktu': 9,                    # Jumat 13:00-14:40
                'ruang': 4,                    # Auditorium (exclusive)
                'priority': 'exclusive',
                'reason': 'Monthly faculty meeting'
            }
        ],
        'preferred_slots': [
            {'waktu': 2},     # Selasa 08:00 (preferred)
            {'waktu': 4},     # Rabu 08:00 (preferred)
            {'waktu': 6}      # Kamis 08:00 (preferred)
        ],
        'blocked_slots': [
            {'waktu': 8, 'reason': 'Jumatan (Friday prayer)'},
            {'waktu': 7, 'reason': 'Hospital duty as medical consultant'},
            {'waktu': 10, 'reason': 'Weekend - no teaching'}
        ]
    }
}

# ===================================================================
# SCENARIO 2: DOSEN MUDA DENGAN FLEKSIBILITAS TINGGI
# ===================================================================

dosen_muda_config = {
    'Dr. Lisa Sari Purnama': {
        'reserved_slots': [],  # Tidak ada slot eksklusif (masih junior)
        
        'preferred_slots': [
            {'waktu': 0},     # Senin pagi - fresh start
            {'waktu': 2},     # Selasa pagi - optimal energy
            {'waktu': 4},     # Rabu pagi - good timing
            {'waktu': 6},     # Kamis pagi - acceptable
            {'waktu': 1},     # Senin siang - masih energik
            {'waktu': 3},     # Selasa siang
            {'waktu': 5}      # Rabu siang
        ],
        'blocked_slots': [
            {'waktu': 8, 'reason': 'Jumatan'},
            {'waktu': 9, 'reason': 'Family time - afternoon'},
            {'waktu': 10, 'reason': 'Weekend - research time'},
            {'waktu': 7, 'reason': 'Kamis siang - not preferred'}
        ]
    }
}

# ===================================================================
# SCENARIO 3: DOSEN PRAKTISI (PART-TIME) DENGAN BATASAN KETAT
# ===================================================================

dosen_praktisi_config = {
    'Dr. Bambang Praktek': {
        'reserved_slots': [
            {
                'waktu': 1,                    # Senin 10:00-11:40
                'priority': 'exclusive',
                'reason': 'Hospital clinic practice - cannot be moved'
            }
        ],
        'preferred_slots': [
            {'waktu': 0},     # Senin 08:00 - before clinic
            {'waktu': 2}      # Selasa 08:00 - ideal timing
        ],
        'blocked_slots': [
            {'waktu': 3, 'reason': 'Clinic duty - afternoon shift'},
            {'waktu': 4, 'reason': 'Clinic duty - afternoon shift'},
            {'waktu': 5, 'reason': 'Clinic duty - afternoon shift'},
            {'waktu': 6, 'reason': 'Clinic duty - afternoon shift'},
            {'waktu': 7, 'reason': 'Clinic duty - afternoon shift'},
            {'waktu': 8, 'reason': 'Jumatan'},
            {'waktu': 9, 'reason': 'Clinic duty - afternoon shift'},
            {'waktu': 10, 'reason': 'Weekend - clinic duty'}
        ]
    }
}

# ===================================================================
# SCENARIO 4: DOSEN DENGAN JADWAL RESEARCH INTENSIF
# ===================================================================

dosen_peneliti_config = {
    'Dr. Ahmad Hidayat': {
        'reserved_slots': [
            {
                'waktu': 2,                    # Selasa 08:00-09:40
                'ruang': 0,                    # Lab Komputer 1
                'priority': 'exclusive',
                'reason': 'Algorithm research lab session - equipment exclusive access'
            }
        ],
        'preferred_slots': [
            {'waktu': 0},     # Senin pagi - fresh mind
            {'waktu': 4},     # Rabu pagi - after research day
            {'waktu': 1},     # Senin siang - still good
            {'waktu': 6}      # Kamis pagi - acceptable
        ],
        'blocked_slots': [
            {'waktu': 8, 'reason': 'Jumatan'},
            {'waktu': 3, 'reason': 'Research meeting with students'},
            {'waktu': 5, 'reason': 'Paper writing dedicated time'}
        ]
    }
}

# ===================================================================
# SCENARIO 5: KEPALA JURUSAN DENGAN TUGAS ADMINISTRATIF
# ===================================================================

kepala_jurusan_config = {
    'Prof. Dr. Budi Santoso': {
        'reserved_slots': [
            {
                'waktu': 3,                    # Selasa 10:00-11:40
                'ruang': 2,                    # Ruang Kelas A
                'priority': 'exclusive',
                'reason': 'Weekly department meeting - head of department'
            },
            {
                'waktu': 7,                    # Kamis 10:00-11:40
                'priority': 'exclusive',
                'reason': 'Academic committee meeting - any available room'
            }
        ],
        'preferred_slots': [
            {'waktu': 1},     # Senin siang - good energy
            {'waktu': 5},     # Rabu siang - mid-week
            {'waktu': 6}      # Kamis pagi - before meeting
        ],
        'blocked_slots': [
            {'waktu': 8, 'reason': 'Jumatan'},
            {'waktu': 0, 'reason': 'Administrative work - early morning'},
            {'waktu': 9, 'reason': 'Dean meeting preparation'},
            {'waktu': 10, 'reason': 'Weekend - family time'}
        ]
    }
}

# ===================================================================
# SCENARIO 6: DOSEN DENGAN KELAS MALAM/SORE
# ===================================================================

dosen_sore_config = {
    'Dr. Citra Dewi': {
        'reserved_slots': [],  # Tidak ada reserved khusus
        
        'preferred_slots': [
            {'waktu': 7},     # Kamis 10:00 - peak afternoon
            {'waktu': 9},     # Jumat 13:00 - afternoon class
            {'waktu': 5}      # Rabu 10:00 - late morning
        ],
        'blocked_slots': [
            {'waktu': 0, 'reason': 'Morning routine - not available early'},
            {'waktu': 2, 'reason': 'Morning routine - not available early'},
            {'waktu': 4, 'reason': 'Morning routine - not available early'},
            {'waktu': 6, 'reason': 'Morning routine - not available early'},
            {'waktu': 8, 'reason': 'Jumatan'},
            {'waktu': 10, 'reason': 'Weekend - family time'}
        ]
    }
}

# ===================================================================
# COMBINING ALL CONFIGURATIONS
# ===================================================================

# Master configuration yang bisa digunakan langsung dalam sistem
preferensi_dosen_enhanced = {
    **profesor_senior_config,
    **dosen_muda_config, 
    **dosen_praktisi_config,
    **dosen_peneliti_config,
    **kepala_jurusan_config,
    **dosen_sore_config
}

# ===================================================================
# UTILITY FUNCTIONS UNTUK VALIDASI KONFIGURASI
# ===================================================================

def validate_preferences_config(config):
    """
    Validasi konfigurasi preferensi dosen untuk mencegah error
    """
    errors = []
    
    for dosen_name, prefs in config.items():
        # Validate reserved slots
        for slot in prefs.get('reserved_slots', []):
            if 'waktu' not in slot:
                errors.append(f"{dosen_name}: reserved_slot missing 'waktu' field")
            if slot.get('priority') != 'exclusive':
                errors.append(f"{dosen_name}: reserved_slot must have priority='exclusive'")
        
        # Validate preferred slots - no priority levels needed anymore
        # Just check that slots have required waktu field
        for slot in prefs.get('preferred_slots', []):
            if 'waktu' not in slot:
                errors.append(f"{dosen_name}: preferred_slot missing 'waktu' field")
        
        # Check for conflicts between reserved and blocked
        reserved_times = [slot['waktu'] for slot in prefs.get('reserved_slots', [])]
        blocked_times = [slot['waktu'] for slot in prefs.get('blocked_slots', [])]
        conflicts = set(reserved_times) & set(blocked_times)
        
        if conflicts:
            errors.append(f"{dosen_name}: conflict between reserved and blocked slots: {conflicts}")
    
    return errors

def generate_weight_summary(config):
    """
    Generate summary of weight distribution untuk analisis
    """
    weights = {'exclusive': 0, 'preferred': 0, 'blocked': 0}
    
    for dosen_name, prefs in config.items():
        weights['exclusive'] += len(prefs.get('reserved_slots', []))
        weights['preferred'] += len(prefs.get('preferred_slots', []))
        weights['blocked'] += len(prefs.get('blocked_slots', []))
    
    return weights

def get_dosen_availability_matrix(config, total_time_slots=11):
    """
    Generate matrix ketersediaan dosen untuk visualisasi
    """
    matrix = {}
    
    for dosen_name, prefs in config.items():
        availability = ['available'] * total_time_slots
        
        # Mark reserved slots
        for slot in prefs.get('reserved_slots', []):
            if slot['waktu'] < total_time_slots:
                availability[slot['waktu']] = 'reserved'
        
        # Mark blocked slots  
        for slot in prefs.get('blocked_slots', []):
            if slot['waktu'] < total_time_slots:
                availability[slot['waktu']] = 'blocked'
        
        # Mark preferred slots
        for slot in prefs.get('preferred_slots', []):
            if slot['waktu'] < total_time_slots and availability[slot['waktu']] == 'available':
                availability[slot['waktu']] = f"preferred_{slot['priority']}"
                
        # Note: flexible_slots removed - simplified to 3 levels only
        
        matrix[dosen_name] = availability
    
    return matrix

# ===================================================================
# EXAMPLE USAGE
# ===================================================================

if __name__ == "__main__":
    # Validate configuration
    validation_errors = validate_preferences_config(preferensi_dosen_enhanced)
    if validation_errors:
        print("❌ Configuration Errors Found:")
        for error in validation_errors:
            print(f"  - {error}")
    else:
        print("✅ Configuration is valid!")
    
    # Generate weight summary
    weight_summary = generate_weight_summary(preferensi_dosen_enhanced)
    print(f"\n📊 Weight Distribution Summary:")
    for priority, count in weight_summary.items():
        print(f"  {priority}: {count} slots")
    
    # Generate availability matrix
    availability_matrix = get_dosen_availability_matrix(preferensi_dosen_enhanced)
    print(f"\n🗓️  Dosen Availability Matrix:")
    print("Dosen" + " " * 25 + "Time Slots (0-10)")
    print("-" * 70)
    for dosen, availability in availability_matrix.items():
        dosen_short = dosen[:25].ljust(25)
        slots_str = " ".join([slot[:3] for slot in availability])
        print(f"{dosen_short} {slots_str}")
    
    print(f"\n✨ Total Dosen Configured: {len(preferensi_dosen_enhanced)}")
    print("Configuration ready to use in scheduling system!")