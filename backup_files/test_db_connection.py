#!/usr/bin/env python3

from dbConfig import db, GetAllDB, get_kuliah_with_dosen_info, get_schedule_data

def test_connection():
    """Test database connection and basic queries"""
    print("Testing database connection...")
    
    if db.connect():
        print("✓ Database connection successful!")
        
        # Test basic queries with actual table names
        tables = ['dosen', 'kuliah', 'ruangan', 'waktu']
        
        for table in tables:
            try:
                data = GetAllDB(table)
                print(f"✓ Table '{table}': {len(data)} records found")
                
                # Show first record as sample
                if data:
                    print(f"  Sample record: {data[0]}")
                    
            except Exception as e:
                print(f"✗ Error querying table '{table}': {e}")
        
        print("\n--- Testing joined queries ---")
        
        # Test kuliah with dosen info
        try:
            kuliah_dosen = get_kuliah_with_dosen_info()
            print(f"✓ Kuliah with dosen info: {len(kuliah_dosen)} records")
            if kuliah_dosen:
                print(f"  Sample: {kuliah_dosen[0]}")
        except Exception as e:
            print(f"✗ Error getting kuliah with dosen info: {e}")
        
        # Test get all schedule data
        try:
            schedule_data = get_schedule_data()
            print(f"✓ Complete schedule data loaded:")
            for key, value in schedule_data.items():
                print(f"  - {key}: {len(value)} records")
        except Exception as e:
            print(f"✗ Error getting schedule data: {e}")
        
        db.disconnect()
        print("\nDatabase connection closed.")
        
    else:
        print("✗ Failed to connect to database. Please check your credentials.")

if __name__ == "__main__":
    test_connection()