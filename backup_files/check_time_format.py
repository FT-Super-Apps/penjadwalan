#!/usr/bin/env python3

from dbConfig import GetAllDB
from datetime import datetime, timedelta

def analyze_time_format():
    """Analyze current time format in database"""
    print("Analyzing time format in database...")
    
    waktu_data = GetAllDB('waktu')
    
    if not waktu_data:
        print("No time data found")
        return
    
    print(f"Found {len(waktu_data)} time slots:")
    
    # Group by day
    days_data = {}
    for row in waktu_data:
        day = row['nama_hari']
        if day not in days_data:
            days_data[day] = []
        days_data[day].append({
            'kode_waktu': row['kode_waktu'],
            'waktu': row['waktu']
        })
    
    # Sort each day by time
    for day in days_data:
        days_data[day].sort(key=lambda x: x['waktu'])
    
    # Display current format
    for day, times in days_data.items():
        print(f"\n{day}:")
        for i, time_slot in enumerate(times):
            print(f"  Index {i}: {time_slot['waktu']} (kode: {time_slot['kode_waktu']})")
    
    # Calculate intervals
    print("\n--- Time Intervals Analysis ---")
    for day, times in days_data.items():
        if len(times) > 1:
            print(f"\n{day} intervals:")
            for i in range(len(times) - 1):
                time1 = datetime.strptime(times[i]['waktu'], '%H:%M')
                time2 = datetime.strptime(times[i+1]['waktu'], '%H:%M')
                diff = time2 - time1
                minutes = diff.total_seconds() / 60
                print(f"  {times[i]['waktu']} -> {times[i+1]['waktu']}: {minutes} minutes")

def create_50_minute_schedule():
    """Create a new time schedule with 50-minute intervals starting from Senin index 0"""
    print("\n--- Creating 50-minute interval schedule ---")
    
    days = ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT']
    start_time = datetime.strptime('07:00', '%H:%M')  # Start at 7:00 AM
    slots_per_day = 7  # 7 slots per day
    
    schedule = {}
    global_index = 0
    
    for day in days:
        schedule[day] = []
        for slot in range(slots_per_day):
            current_time = start_time + timedelta(minutes=slot * 50)
            schedule[day].append({
                'global_index': global_index,
                'day_index': slot,
                'time': current_time.strftime('%H:%M'),
                'day': day
            })
            global_index += 1
    
    # Display new schedule
    print("Proposed 50-minute interval schedule:")
    for day, slots in schedule.items():
        print(f"\n{day} (indices {slots[0]['global_index']}-{slots[-1]['global_index']}):")
        for slot in slots:
            print(f"  Global Index {slot['global_index']:2d} | Day Index {slot['day_index']} | {slot['time']}")
    
    return schedule

if __name__ == "__main__":
    analyze_time_format()
    create_50_minute_schedule()