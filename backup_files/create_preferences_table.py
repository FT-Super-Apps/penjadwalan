#!/usr/bin/env python3

from dbConfig import db

def create_referensi_waktu_dosen_table():
    """Create referensi_waktu_dosen table in the database"""
    print("Creating referensi_waktu_dosen table...")
    
    if not db.connect():
        print("✗ Failed to connect to database")
        return False
    
    try:
        cursor = db.connection.cursor()
        
        # Create table SQL
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS referensi_waktu_dosen (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nidn VARCHAR(255) NOT NULL,
            nama_dosen VARCHAR(255) NOT NULL,
            hari ENUM('SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU') NOT NULL,
            waktu_suka JSON,
            waktu_tidak_bisa JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (nidn) REFERENCES dosen(nidn) ON DELETE CASCADE,
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
        
        # Sample preferences data
        sample_preferences = [
            {
                'nidn': '0125017702',
                'nama_dosen': 'ANDI SALSA ANGGERAINI',
                'hari': 'SENIN',
                'waktu_suka': '[1, 2, 3]',  # Kode waktu 1, 2, 3 (07:00, 07:50, 08:40)
                'waktu_tidak_bisa': '[6, 7]'  # Kode waktu 6, 7 (11:10, 12:00)
            },
            {
                'nidn': '0901037802',
                'nama_dosen': 'ANDI NILAWATI',
                'hari': 'SELASA',
                'waktu_suka': '[8, 9, 10]',  # Selasa 07:00, 07:50, 08:40
                'waktu_tidak_bisa': '[13, 14]'  # Selasa 11:10, 12:00
            },
            {
                'nidn': '0125017702',
                'nama_dosen': 'ANDI SALSA ANGGERAINI',
                'hari': 'RABU',
                'waktu_suka': '[15, 16]',  # Rabu 07:00, 07:50
                'waktu_tidak_bisa': '[20, 21]'  # Rabu 11:10, 12:00
            }
        ]
        
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
        
        # Check data
        cursor.execute("SELECT * FROM referensi_waktu_dosen")
        data = cursor.fetchall()
        
        print(f"\nFound {len(data)} preference records:")
        for record in data:
            print(f"  - {record['nama_dosen']} ({record['hari']})")
            print(f"    Suka: {record['waktu_suka']}")
            print(f"    Tidak bisa: {record['waktu_tidak_bisa']}")
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"✗ Error verifying table: {e}")
        return False
    
    finally:
        db.disconnect()

def main():
    """Main function to create and set up referensi_waktu_dosen table"""
    print("=== Setting up Referensi Waktu Dosen Table ===\n")
    
    # Step 1: Create table
    if create_referensi_waktu_dosen_table():
        print()
        
        # Step 2: Add sample data
        if add_sample_preferences():
            print()
            
            # Step 3: Verify everything
            verify_table()
            
            print("\n🎉 Referensi Waktu Dosen table setup completed!")
            print("   - Table created with proper structure")
            print("   - Sample preferences added")
            print("   - Foreign key relationship with dosen table")
        else:
            print("\n⚠️  Table created but failed to add sample data")
    else:
        print("\n✗ Failed to create table")

if __name__ == "__main__":
    main()