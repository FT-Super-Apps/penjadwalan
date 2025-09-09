#!/usr/bin/env python3

from dbConfig import db, GetAllDB
from datetime import datetime, timedelta
import json

def backup_current_waktu():
    """Backup current waktu table data"""
    print("Creating backup of current waktu table...")
    
    current_data = GetAllDB('waktu')
    
    if current_data:
        # Save to JSON file
        backup_file = 'backup_waktu_original.json'
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(current_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Backup saved to {backup_file} ({len(current_data)} records)")
        return True
    else:
        print("✗ No data found to backup")
        return False

def create_new_waktu_data():
    """Create new waktu data with 50-minute intervals"""
    print("Creating new waktu data with 50-minute intervals...")
    
    days = ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU']
    start_time = datetime.strptime('07:00', '%H:%M')
    slots_per_day = 7  # 7 slots per day
    
    new_waktu_data = []
    kode_waktu = 1
    
    for day in days:
        for slot in range(slots_per_day):
            current_time = start_time + timedelta(minutes=slot * 50)
            new_waktu_data.append({
                'kode_waktu': str(kode_waktu),
                'nama_hari': day,
                'waktu': current_time.strftime('%H:%M')
            })
            kode_waktu += 1
    
    print(f"✓ Created {len(new_waktu_data)} new time slots")
    return new_waktu_data

def update_waktu_table():
    """Update waktu table with new 50-minute interval data"""
    if not db.connect():
        print("✗ Failed to connect to database")
        return False
    
    try:
        cursor = db.connection.cursor()
        
        # Clear existing data
        print("Clearing existing waktu data...")
        cursor.execute("DELETE FROM waktu")
        print(f"✓ Removed existing records")
        
        # Insert new data
        print("Inserting new 50-minute interval data...")
        new_data = create_new_waktu_data()
        
        insert_query = """
        INSERT INTO waktu (kode_waktu, nama_hari, waktu) 
        VALUES (%s, %s, %s)
        """
        
        for record in new_data:
            cursor.execute(insert_query, (
                record['kode_waktu'],
                record['nama_hari'], 
                record['waktu']
            ))
        
        # Commit changes
        db.connection.commit()
        cursor.close()
        
        print(f"✓ Successfully inserted {len(new_data)} new records")
        return True
        
    except Exception as e:
        print(f"✗ Error updating waktu table: {e}")
        if db.connection:
            db.connection.rollback()
        return False
    
    finally:
        db.disconnect()

def verify_update():
    """Verify the updated waktu table"""
    print("\nVerifying updated waktu table...")
    
    waktu_data = GetAllDB('waktu')
    
    if not waktu_data:
        print("✗ No data found after update")
        return False
    
    print(f"✓ Found {len(waktu_data)} records after update")
    
    # Group by day and show structure
    days_data = {}
    for row in waktu_data:
        day = row['nama_hari']
        if day not in days_data:
            days_data[day] = []
        days_data[day].append(row)
    
    # Sort each day by kode_waktu
    for day in days_data:
        days_data[day].sort(key=lambda x: int(x['kode_waktu']))
    
    print("\nNew waktu table structure:")
    for day, times in days_data.items():
        print(f"\n{day}:")
        for i, time_slot in enumerate(times):
            print(f"  Index {i}: {time_slot['waktu']} (kode: {time_slot['kode_waktu']})")
    
    # Verify 50-minute intervals
    print("\n--- Verifying 50-minute intervals ---")
    for day, times in days_data.items():
        if len(times) > 1:
            print(f"\n{day} intervals:")
            for i in range(len(times) - 1):
                time1 = datetime.strptime(times[i]['waktu'], '%H:%M')
                time2 = datetime.strptime(times[i+1]['waktu'], '%H:%M')
                diff = time2 - time1
                minutes = diff.total_seconds() / 60
                status = "✓" if minutes == 50 else "✗"
                print(f"  {status} {times[i]['waktu']} -> {times[i+1]['waktu']}: {minutes} minutes")
    
    return True

def main():
    """Main function to update database with 50-minute intervals"""
    print("=== Updating Database Waktu Table to 50-Minute Intervals ===\n")
    
    # Step 1: Backup current data
    if not backup_current_waktu():
        print("Warning: Could not create backup, but continuing...")
    
    # Step 2: Update table
    if update_waktu_table():
        print("\n✓ Database update completed successfully")
        
        # Step 3: Verify update
        verify_update()
        
        print("\n🎉 Waktu table successfully updated to 50-minute intervals!")
        print("   - Senin[0] = 07:00, Senin[1] = 07:50, etc.")
        print("   - Each day has 7 time slots with 50-minute intervals")
        
    else:
        print("\n✗ Database update failed")

if __name__ == "__main__":
    main()