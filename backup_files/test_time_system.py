#!/usr/bin/env python3

from dbConfig import get_schedule_data, create_50_minute_time_slots, map_database_time_to_array

def test_time_system():
    """Test the new 50-minute interval time system"""
    print("Testing 50-minute interval time system...")
    
    # Get all schedule data
    schedule_data = get_schedule_data()
    
    print("\n=== Database Time Slots (Original) ===")
    waktu_db = schedule_data['waktu']
    print(f"Total slots in database: {len(waktu_db)}")
    
    # Show first few entries
    for i, waktu in enumerate(waktu_db[:10]):
        print(f"{i+1:2d}. {waktu['nama_hari']:6s} {waktu['waktu']} (kode: {waktu['kode_waktu']})")
    
    print("\n=== 50-Minute Interval System (New) ===")
    waktu_50 = schedule_data['waktu_50_minutes']
    print(f"Total 50-minute slots: {len(waktu_50)}")
    
    # Show all entries grouped by day
    current_day = None
    for slot in waktu_50:
        if slot['hari'] != current_day:
            current_day = slot['hari']
            print(f"\n{current_day}:")
        
        print(f"  Index {slot['global_index']:2d} | Day {slot['day_index']} | {slot['jam_mulai']}")
    
    print("\n=== Time Mapping (Database to Array) ===")
    time_mapping = schedule_data['time_mapping']
    print(f"Time mappings created: {len(time_mapping)}")
    
    # Show mapping for each day
    days = ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU']
    for day in days:
        day_mappings = [
            (kode, data) for kode, data in time_mapping.items() 
            if data['hari'] == day
        ]
        
        if day_mappings:
            print(f"\n{day} mappings:")
            day_mappings.sort(key=lambda x: x[1]['waktu'])
            for kode, data in day_mappings:
                print(f"  DB Code {kode} -> Array Index {data['array_index']} | {data['waktu']}")

def demonstrate_usage():
    """Demonstrate how to use the time system"""
    print("\n\n=== Usage Examples ===")
    
    # Example 1: Convert Senin index 0 (should be 07:00)
    waktu_50 = create_50_minute_time_slots()
    senin_0 = waktu_50[0]  # Global index 0 = Senin index 0
    print(f"Senin Array Index 0: {senin_0['jam_mulai']} ({senin_0['hari']})")
    
    # Example 2: Show progression with 50-minute intervals
    print("\nProgression of 50-minute intervals on Senin:")
    for i in range(7):  # 7 slots per day
        slot = waktu_50[i]
        print(f"  Senin[{i}] = Global[{slot['global_index']}] = {slot['jam_mulai']}")
    
    # Example 3: Show all days index 0
    print("\nAll days at index 0 (07:00):")
    days = ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT']
    for day_idx, day in enumerate(days):
        global_idx = day_idx * 7  # 7 slots per day
        slot = waktu_50[global_idx]
        print(f"  {day}[0] = Global[{global_idx}] = {slot['jam_mulai']}")

if __name__ == "__main__":
    test_time_system()
    demonstrate_usage()