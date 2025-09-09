# 🚀 Installation & Setup Guide

Panduan lengkap instalasi dan konfigurasi Enhanced University Scheduling System.

## 📋 System Requirements

### Minimum Requirements
- **Python**: 3.8+ (recommended 3.9+)
- **RAM**: 2GB (untuk dataset kecil < 100 mata kuliah)
- **Storage**: 100MB free space
- **OS**: Windows 10/11, macOS 10.14+, Ubuntu 18.04+

### Recommended Requirements  
- **Python**: 3.10+
- **RAM**: 4GB+ (untuk dataset besar > 200 mata kuliah)
- **Storage**: 500MB free space
- **Database**: MySQL 8.0+, PostgreSQL 12+, atau SQLite 3.35+

## 🛠 Step-by-Step Installation

### Step 1: Clone Repository
```bash
git clone https://github.com/your-repo/enhanced-scheduling.git
cd enhanced-scheduling
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux  
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**requirements.txt** (create if not exists):
```
psutil>=5.8.0
colorama>=0.4.4
mysql-connector-python>=8.0.29  # For MySQL
psycopg2-binary>=2.9.3          # For PostgreSQL
```

### Step 4: Database Setup

#### Option A: SQLite (Simple, for testing)
```python
# No additional setup needed
# dbConfig.py will use mock data by default
```

#### Option B: MySQL Setup
```bash
# Install MySQL (if not installed)
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server

# Windows: Download from https://dev.mysql.com/downloads/mysql/
# macOS: brew install mysql
```

**Create database and user:**
```sql
CREATE DATABASE scheduling_system;
CREATE USER 'scheduling_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON scheduling_system.* TO 'scheduling_user'@'localhost';
FLUSH PRIVILEGES;
```

#### Option C: PostgreSQL Setup
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# Windows: Download from https://www.postgresql.org/download/
# macOS: brew install postgresql
```

**Create database:**
```sql
CREATE DATABASE scheduling_system;
CREATE USER scheduling_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE scheduling_system TO scheduling_user;
```

### Step 5: Import Database Schema
```bash
# For MySQL
mysql -u scheduling_user -p scheduling_system < database_schema.sql

# For PostgreSQL  
psql -U scheduling_user -d scheduling_system -f database_schema.sql

# For SQLite (auto-created when running)
# No manual import needed
```

### Step 6: Configure Database Connection

**Create/Edit `dbConfig.py`:**

```python
import mysql.connector
# or import psycopg2 for PostgreSQL

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'scheduling_user',
    'password': 'your_password',
    'database': 'scheduling_system',
    'port': 3306  # 5432 for PostgreSQL
}

def GetAllDB(table_name):
    """Get data from database"""
    try:
        # MySQL connection
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(f"SELECT * FROM {table_name}")
        result = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return result
        
    except Exception as e:
        print(f"Database error: {e}")
        # Fallback to mock data
        return get_mock_data(table_name)

def GenerateData(raw_data):
    """Convert database data to expected format"""
    result = []
    
    for item in raw_data:
        if 'hari' in item and 'jam_mulai' in item:
            result.append([item['id'], item['hari'], item['jam_mulai']])
        elif 'nama' in item and 'kapasitas' in item:
            result.append([item['id'], item['nama'], item['kapasitas']])
        elif 'nama' in item and 'dosen' in item and 'sks' in item:
            result.append(item)
    
    return result

def get_mock_data(table_name):
    """Fallback mock data when database not available"""
    # ... (existing mock data implementation)
```

## ⚙️ Configuration

### Step 7: Configure Enhanced Preferences

**Edit preferences in main file:**
```python
# Copy from examples/enhanced_preferences_config.py
from examples.enhanced_preferences_config import preferensi_dosen_enhanced

# Or define directly:
preferensi_dosen_enhanced = {
    'Your Lecturer Name': {
        'reserved_slots': [
            {'waktu': 1, 'ruang': 0, 'priority': 'exclusive', 'reason': 'Weekly meeting'}
        ],
        'preferred_slots': [
            {'waktu': 2, 'priority': 'high'}
        ],
        'blocked_slots': [
            {'waktu': 8, 'reason': 'Prayer time'}
        ],
        'flexible_slots': [
            {'waktu': 4, 'priority': 'medium'}
        ]
    }
}
```

### Step 8: Adjust Algorithm Parameters
```python
# Algorithm settings (in jadwal-non-paralel.py)
jml_kromosom = 10           # Population size (increase for better results)
max_generataion = 20        # Max generations (increase for complex scheduling)
crossover_rate = 75         # Crossover rate (75-85% recommended)
mutation_rate = 25          # Mutation rate (20-30% recommended)

# Weight penalties (adjust based on your priorities)
preference_weights = {
    'exclusive': 1000,      # Reserved slots (highest penalty)
    'high': 50,            # High priority preferences  
    'medium': 30,          # Medium priority
    'low': 10             # Low priority
}
```

## 🧪 Testing Installation

### Quick Test
```bash
python jadwal-non-paralel.py
```

**Expected output:**
```
=== INITIALIZING ENHANCED SCHEDULING SYSTEM ===
Pre-allocated X reserved slots
==================================================
GENERASI KE-1
==================================================
...
✅ Success achieved: Yes
```

### Advanced Testing
```python
# Test with your actual data
python examples/enhanced_preferences_config.py

# Expected output:
# ✅ Configuration is valid!
# 📊 Weight Distribution Summary:
# ...
```

### Validate Database Connection
```python
# Create test_db.py
from dbConfig import GetAllDB, GenerateData

# Test database connection
try:
    kuliah_data = GetAllDB('kuliah_teknik')
    print(f"✅ Database connected! Found {len(kuliah_data)} courses")
except Exception as e:
    print(f"❌ Database error: {e}")
```

## 🐛 Troubleshooting

### Common Issues

#### 1. "ModuleNotFoundError: No module named 'psutil'"
```bash
pip install psutil colorama
```

#### 2. "Database connection failed"
- Check database credentials in `dbConfig.py`
- Ensure database server is running
- Verify user permissions
- Test connection manually:
```bash
mysql -u scheduling_user -p
# or
psql -U scheduling_user -d scheduling_system
```

#### 3. "Reserved slot conflicts detected"
- Check `preferensi_dosen_enhanced` configuration
- Ensure no two lecturers reserve the same slot
- Use validation function:
```python
from examples.enhanced_preferences_config import validate_preferences_config
errors = validate_preferences_config(preferensi_dosen_enhanced)
print(errors)
```

#### 4. "Low fitness scores / No solution found"
- Increase `max_generataion` (try 50-100)
- Increase `jml_kromosom` (try 20-50)  
- Reduce reserved slots
- Add more flexible slots
- Lower penalty weights

#### 5. "Memory issues with large datasets"
- Reduce population size (`jml_kromosom`)
- Implement data pagination
- Add garbage collection:
```python
import gc
gc.collect()  # Add after each generation
```

### Performance Optimization

#### For Large Datasets (500+ courses)
```python
# Increase algorithm parameters
jml_kromosom = 50
max_generataion = 100
crossover_rate = 80
mutation_rate = 20

# Enable parallel processing (advanced)
import multiprocessing as mp
mp.set_start_method('spawn')  # For Windows compatibility
```

#### Memory Optimization
```python
# Clear cache periodically
timeClash.clear()  # Add every 10 generations
objectFitnes.clear()
```

### Logging Setup (Optional)
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduling.log'),
        logging.StreamHandler()
    ]
)
```

## 🔄 Updates & Maintenance

### Regular Maintenance
1. **Database cleanup** (monthly):
```sql
CALL ClearOldSchedulingData(30);  -- Remove data older than 30 days
```

2. **Backup preferences**:
```bash
mysqldump -u scheduling_user -p scheduling_system reserved_slots preferred_slots blocked_slots flexible_slots > preferences_backup.sql
```

3. **Performance monitoring**:
```python
# Monitor RAM usage and execution time
# Add alerts if performance degrades
```

### Updating Preferences
```python
# Backup current preferences before changes
import json
with open('preferences_backup.json', 'w') as f:
    json.dump(preferensi_dosen_enhanced, f, indent=2)

# Update preferences
# Test with small dataset first
# Deploy to production
```

## 📞 Support & Help

### Getting Help
1. Check troubleshooting section above
2. Review logs in `scheduling.log`
3. Test with minimal dataset
4. Open issue on GitHub with:
   - Error message
   - Your configuration
   - System information
   - Steps to reproduce

### Documentation
- **README.md**: Overview and features
- **database_schema.sql**: Database structure
- **examples/**: Configuration examples
- **API documentation**: (if implementing web interface)

---

**Installation Complete! 🎉**

Your enhanced scheduling system is ready to optimize university course scheduling with reserved slots and intelligent preference handling.