#!/usr/bin/env python3

from dbConfig import db

def check_database_structure():
    """Check all tables and their structures in the database"""
    print("Checking database structure...")
    
    if not db.connect():
        print("✗ Failed to connect to database")
        return
    
    # Get all tables
    tables_query = "SHOW TABLES"
    tables_result = db.execute_query(tables_query)
    
    if not tables_result:
        print("No tables found in database")
        return
    
    print(f"Found {len(tables_result)} tables:")
    
    for table_row in tables_result:
        table_name = list(table_row.values())[0]
        print(f"\n📋 Table: {table_name}")
        
        # Get table structure
        describe_query = f"DESCRIBE {table_name}"
        structure = db.execute_query(describe_query)
        
        if structure:
            print("   Columns:")
            for col in structure:
                print(f"   - {col['Field']} ({col['Type']}) {'NOT NULL' if col['Null'] == 'NO' else 'NULL'}")
        
        # Get sample data
        sample_query = f"SELECT * FROM {table_name} LIMIT 3"
        sample_data = db.execute_query(sample_query)
        
        if sample_data:
            print(f"   Sample data ({len(sample_data)} records):")
            for i, row in enumerate(sample_data, 1):
                print(f"   {i}. {row}")
        else:
            print("   No data found")
    
    db.disconnect()
    print("\nDatabase structure check completed.")

if __name__ == "__main__":
    check_database_structure()