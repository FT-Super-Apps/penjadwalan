import mysql.connector
import os
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', 3306))
        self.database = os.getenv('DB_NAME', 'penjadwalan_db')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            return True
        except mysql.connector.Error as err:
            print(f"Error connecting to MySQL database: {err}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def execute_query(self, query, params=None):
        """Execute a SELECT query and return results"""
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return None
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            cursor.close()
            return results
        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
            return None

# Global database connection instance
db = DatabaseConnection()

def GetAllDB(table_name):
    """Fetch all records from specified table based on actual database schema"""
    
    # Define table queries based on actual database structure
    queries = {
        'dosen': "SELECT nidn, nama, kode_prodi FROM dosen ORDER BY nama",
        'kuliah': "SELECT kode_kuliah, kode_matakuliah, kode_dosen, nama_kelas, kode_prodi, sks FROM kuliah ORDER BY kode_kuliah",
        'ruangan': "SELECT id, nama_ruangan FROM ruangan ORDER BY id",
        'waktu': "SELECT kode_waktu, nama_hari, waktu FROM waktu ORDER BY kode_waktu"
    }
    
    if table_name not in queries:
        print(f"Unknown table: {table_name}. Available tables: {list(queries.keys())}")
        return []
    
    # Execute query
    results = db.execute_query(queries[table_name])
    
    if results is None:
        print(f"Failed to fetch data from {table_name}")
        return []
    
    return results

def get_kuliah_with_dosen_info():
    """Get kuliah data joined with dosen information"""
    query = """
    SELECT 
        k.kode_kuliah,
        k.kode_matakuliah, 
        k.nama_kelas,
        k.sks,
        k.kode_prodi,
        d.nama as nama_dosen,
        d.nidn
    FROM kuliah k
    LEFT JOIN dosen d ON k.kode_dosen = d.nidn
    ORDER BY k.kode_kuliah
    """
    
    results = db.execute_query(query)
    return results if results else []

def create_50_minute_time_slots():
    """Create standardized 50-minute interval time slots"""
    from datetime import datetime, timedelta
    
    days = ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT']
    start_time = datetime.strptime('07:00', '%H:%M')
    slots_per_day = 7  # 7 slots per day with 50-minute intervals
    
    time_slots = []
    global_index = 0
    
    for day in days:
        for slot in range(slots_per_day):
            current_time = start_time + timedelta(minutes=slot * 50)
            time_slots.append({
                'id': global_index,
                'hari': day,
                'jam_mulai': current_time.strftime('%H:%M'),
                'day_index': slot,
                'global_index': global_index
            })
            global_index += 1
    
    return time_slots

def map_database_time_to_array():
    """Map database time slots to array indices for scheduling algorithm"""
    waktu_data = GetAllDB('waktu')
    
    # Create mapping from database kode_waktu to array index
    time_mapping = {}
    
    # Sort by day and time for consistent mapping
    sorted_waktu = sorted(waktu_data, key=lambda x: (
        ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU'].index(x['nama_hari']),
        x['waktu']
    ))
    
    for idx, waktu in enumerate(sorted_waktu):
        time_mapping[waktu['kode_waktu']] = {
            'array_index': idx,
            'hari': waktu['nama_hari'],
            'waktu': waktu['waktu'],
            'day_index': idx % 5 if waktu['nama_hari'] != 'SABTU' else idx % 6
        }
    
    return time_mapping

def get_schedule_data():
    """Get all data needed for scheduling algorithm"""
    return {
        'dosen': GetAllDB('dosen'),
        'kuliah': get_kuliah_with_dosen_info(),
        'ruangan': GetAllDB('ruangan'),
        'waktu': GetAllDB('waktu'),
        'waktu_50_minutes': create_50_minute_time_slots(),
        'time_mapping': map_database_time_to_array()
    }

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