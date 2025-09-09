#!/usr/bin/env python3

from dbConfig import db

def check_dosen_table_structure():
    """Check the structure of dosen table to understand the foreign key"""
    print("Checking dosen table structure...")
    
    if not db.connect():
        print("✗ Failed to connect to database")
        return None
    
    try:
        cursor = db.connection.cursor(dictionary=True)
        
        # Check table structure
        cursor.execute("DESCRIBE dosen")
        structure = cursor.fetchall()
        
        print("Dosen table structure:")
        for column in structure:
            print(f"  - {column['Field']} ({column['Type']}) {'NOT NULL' if column['Null'] == 'NO' else 'NULL'} {'KEY' if column['Key'] else ''}")
        
        cursor.close()
        return structure
        
    except Exception as e:
        print(f"✗ Error checking dosen table: {e}")
        return None
    
    finally:
        db.disconnect()

def create_referensi_waktu_dosen_table_fixed():
    """Create referensi_waktu_dosen table without foreign key constraint"""
    print("Creating referensi_waktu_dosen table (without foreign key)...")
    
    if not db.connect():
        print("✗ Failed to connect to database")
        return False
    
    try:
        cursor = db.connection.cursor()
        
        # Drop table if exists
        cursor.execute("DROP TABLE IF EXISTS referensi_waktu_dosen")
        
        # Create table SQL without foreign key constraint
        create_table_sql = """
        CREATE TABLE referensi_waktu_dosen (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nidn VARCHAR(255) NOT NULL,
            nama_dosen VARCHAR(255) NOT NULL,
            hari ENUM('SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU') NOT NULL,
            waktu_suka JSON,
            waktu_tidak_bisa JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_nidn (nidn),
            UNIQUE KEY unique_dosen_hari (nidn, hari)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        cursor.execute(create_table_sql)
        db.connection.commit()
        cursor.close()
        
        print("✓ Table referensi_waktu_dosen created successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Error creating table: {e}")
        if db.connection:
            db.connection.rollback()
        return False
    
    finally:
        db.disconnect()

def add_sample_preferences():
    """Add some sample preferences to the table"""
    print("Adding sample preferences...")
    
    if not db.connect():
        print("✗ Failed to connect to database")
        return False
    
    try:
        cursor = db.connection.cursor()
        
        # Get some real dosen data first
        cursor.execute("SELECT nidn, nama FROM dosen LIMIT 5")
        dosen_list = cursor.fetchall()
        
        if not dosen_list:
            print("✗ No dosen data found")
            return False
        
        # Sample preferences data using real dosen
        sample_preferences = []
        for i, (nidn, nama) in enumerate(dosen_list[:3]):
            days = ['SENIN', 'SELASA', 'RABU']
            day = days[i % 3]
            
            # Calculate waktu codes for the selected day
            day_start = ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU'].index(day) * 7 + 1
            waktu_suka = [day_start, day_start + 1, day_start + 2]  # First 3 slots
            waktu_tidak_bisa = [day_start + 5, day_start + 6]  # Last 2 slots
            
            sample_preferences.append({
                'nidn': nidn,
                'nama_dosen': nama,
                'hari': day,
                'waktu_suka': str(waktu_suka).replace("'", '"'),
                'waktu_tidak_bisa': str(waktu_tidak_bisa).replace("'", '"')
            })
        
        insert_sql = """
        INSERT IGNORE INTO referensi_waktu_dosen 
        (nidn, nama_dosen, hari, waktu_suka, waktu_tidak_bisa) 
        VALUES (%s, %s, %s, %s, %s)
        """
        
        for pref in sample_preferences:
            cursor.execute(insert_sql, (
                pref['nidn'],
                pref['nama_dosen'],
                pref['hari'],
                pref['waktu_suka'],
                pref['waktu_tidak_bisa']
            ))
        
        db.connection.commit()
        cursor.close()
        
        print(f"✓ Added {len(sample_preferences)} sample preferences")
        return True
        
    except Exception as e:
        print(f"✗ Error adding sample preferences: {e}")
        if db.connection:
            db.connection.rollback()
        return False
    
    finally:
        db.disconnect()

def verify_table():
    """Verify the created table and show its structure"""
    print("\nVerifying referensi_waktu_dosen table...")
    
    if not db.connect():
        print("✗ Failed to connect to database")
        return False
    
    try:
        cursor = db.connection.cursor(dictionary=True)
        
        # Check table structure
        cursor.execute("DESCRIBE referensi_waktu_dosen")
        structure = cursor.fetchall()
        
        print("Table structure:")
        for column in structure:
            print(f"  - {column['Field']} ({column['Type']}) {'NOT NULL' if column['Null'] == 'NO' else 'NULL'}")
        
        # Check data with waktu details
        cursor.execute("""
            SELECT r.*, 
                   GROUP_CONCAT(DISTINCT w1.waktu ORDER BY w1.kode_waktu) as waktu_suka_detail,
                   GROUP_CONCAT(DISTINCT w2.waktu ORDER BY w2.kode_waktu) as waktu_tidak_bisa_detail
            FROM referensi_waktu_dosen r
            LEFT JOIN waktu w1 ON FIND_IN_SET(w1.kode_waktu, REPLACE(REPLACE(r.waktu_suka, '[', ''), ']', ''))
            LEFT JOIN waktu w2 ON FIND_IN_SET(w2.kode_waktu, REPLACE(REPLACE(r.waktu_tidak_bisa, '[', ''), ']', ''))
            GROUP BY r.id
        """)
        data = cursor.fetchall()
        
        print(f"\nFound {len(data)} preference records:")
        for record in data:
            print(f"  - {record['nama_dosen']} ({record['hari']})")
            print(f"    Suka: {record['waktu_suka']} → {record['waktu_suka_detail']}")
            print(f"    Tidak bisa: {record['waktu_tidak_bisa']} → {record['waktu_tidak_bisa_detail']}")
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"✗ Error verifying table: {e}")
        return False
    
    finally:
        db.disconnect()

def main():
    """Main function to create and set up referensi_waktu_dosen table"""
    print("=== Setting up Referensi Waktu Dosen Table (Fixed) ===\n")
    
    # Step 1: Check dosen table structure
    check_dosen_table_structure()
    print()
    
    # Step 2: Create table
    if create_referensi_waktu_dosen_table_fixed():
        print()
        
        # Step 3: Add sample data
        if add_sample_preferences():
            print()
            
            # Step 4: Verify everything
            verify_table()
            
            print("\n🎉 Referensi Waktu Dosen table setup completed!")
            print("   - Table created successfully")
            print("   - Sample preferences added with real dosen data")
            print("   - Ready for web interface integration")
        else:
            print("\n⚠️  Table created but failed to add sample data")
    else:
        print("\n✗ Failed to create table")

if __name__ == "__main__":
    main()