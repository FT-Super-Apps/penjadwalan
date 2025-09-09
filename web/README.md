# 🌐 Enhanced Scheduling System - Web Interface

Modern, responsive web interface for the Enhanced University Scheduling System with drag-and-drop file upload, real-time processing, and beautiful result visualization.

## ✨ Features

### 📤 **Smart File Upload**
- **Drag & Drop Interface**: Beautiful upload zones with animation effects
- **Multi-format Support**: CSV, Excel (.xlsx, .xls) files
- **Real-time Validation**: Instant file structure validation
- **Progress Tracking**: Visual progress bars for file processing

### ⚙️ **Advanced Configuration**
- **Algorithm Tuning**: Population size, generations, crossover/mutation rates
- **Preference Weights**: Customizable penalty weights for different violations
- **Constraint Settings**: Flexible optimization parameters
- **Tabbed Interface**: Organized configuration sections

### 📊 **Modern Results Display**
- **Interactive Statistics**: Animated statistics cards
- **Enhanced Schedule Table**: Responsive table with status indicators
- **Visual Status Badges**: Color-coded violation indicators
- **Export Options**: Excel, CSV, PDF export functionality

### 🎨 **Beautiful UI/UX**
- **Glass Morphism Design**: Modern blur effects and gradients
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Dark Mode Support**: Automatic dark theme detection
- **Smooth Animations**: CSS transitions and keyframe animations

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd web
pip install -r requirements.txt
```

### 2. Run Development Server
```bash
python run.py --mode dev
```

### 3. Access the Application
Open your browser and navigate to: `http://localhost:5000`

## 📋 Usage Guide

### Step 1: Upload Data Files
1. **Course Data** (Required)
   - Columns: `nama`, `dosen`, `sks`
   - Example: "Algoritma & Pemrograman", "Dr. Ahmad", 3

2. **Time Slots** (Required)
   - Columns: `hari`, `jam_mulai`
   - Example: "Senin", "08:00"

3. **Room Data** (Required)
   - Columns: `nama`, `kapasitas`
   - Example: "Lab Komputer 1", 30

4. **Lecturer Preferences** (Optional)
   - Columns: `dosen`, `preferensi_waktu`, `tidak_bisa_waktu`
   - Example: "Dr. Ahmad", "[0,2,4]", "[8]"

### Step 2: Configure Settings
- **Algorithm Tab**: Adjust population size, generations, crossover/mutation rates
- **Preferences Tab**: Set penalty weights for different violations
- **Constraints Tab**: Configure optimization approach

### Step 3: Start Optimization
- Click "Start Scheduling Optimization"
- Watch real-time progress updates
- View detailed results and statistics

### Step 4: Export Results
- Export to Excel, CSV, or PDF
- Generate detailed optimization report

## 🏗 Architecture

### Frontend
- **HTML5**: Modern semantic markup
- **CSS3**: Advanced styling with flexbox, grid, animations
- **JavaScript ES6+**: Modern async/await, fetch API, classes
- **Bootstrap 5**: Responsive framework
- **Chart.js**: Data visualization (optional)

### Backend
- **Flask 2.3+**: Python web framework
- **Pandas**: Data processing and file handling
- **NumPy**: Numerical computations
- **Werkzeug**: WSGI utilities and file handling
- **Gunicorn**: Production WSGI server

### File Structure
```
web/
├── app.py                 # Main Flask application
├── enhanced_scheduler.py  # Scheduling algorithm wrapper
├── run.py                # Application launcher
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── static/
│   ├── js/
│   │   └── main.js      # Frontend JavaScript
│   └── css/
│       └── custom.css   # Additional styles
├── templates/
│   └── index.html       # Main HTML template
└── uploads/             # File upload directory
```

## 🔧 Configuration

### Environment Variables
```bash
# Production settings
export SECRET_KEY="your-super-secret-production-key"
export UPLOAD_FOLDER="/path/to/uploads"
export DATABASE_URL="postgresql://user:pass@localhost/scheduling"
export MAX_CONTENT_LENGTH="33554432"  # 32MB

# Development settings
export FLASK_ENV="development"
export FLASK_DEBUG="1"
```

### Algorithm Configuration
```javascript
// Default settings (can be changed in UI)
{
  "algorithm": {
    "populationSize": 10,
    "maxGenerations": 50,
    "crossoverRate": 75,
    "mutationRate": 25,
    "earlyTermination": 0.95,
    "minutesPerSks": 50
  },
  "preferences": {
    "reservedPenalty": 1000,
    "highPenalty": 50,
    "mediumPenalty": 30,
    "lowPenalty": 10,
    "enableEnhanced": true
  },
  "constraints": {
    "clashWeight": 100,
    "allowPartial": true,
    "optimizeFor": "fitness"
  }
}
```

## 🚀 Production Deployment

### Using Gunicorn (Recommended)
```bash
# Install production dependencies
pip install gunicorn gevent

# Run with Gunicorn
python run.py --mode prod --host 0.0.0.0 --port 8000 --workers 4
```

### Using Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["python", "run.py", "--mode", "prod", "--host", "0.0.0.0"]
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    client_max_body_size 32M;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # For file uploads
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }
    
    # Serve static files directly
    location /static/ {
        alias /path/to/your/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## 📊 API Endpoints

### Main Endpoints
- `GET /` - Main application interface
- `POST /api/schedule` - Run scheduling optimization
- `POST /api/export/<format>` - Export results (excel, csv, pdf)
- `POST /api/report` - Generate detailed report
- `GET /health` - Health check endpoint

### Request/Response Examples

#### Schedule Optimization
```javascript
// Request
POST /api/schedule
Content-Type: multipart/form-data

FormData:
- courses: [uploaded CSV/Excel file]
- times: [uploaded CSV/Excel file]  
- rooms: [uploaded CSV/Excel file]
- preferences: [uploaded CSV/Excel file] (optional)
- config: {"algorithm": {...}, "preferences": {...}}

// Response
{
  "schedule": [
    {
      "course": "Algoritma & Pemrograman",
      "lecturer": "Dr. Ahmad",
      "day": "Senin",
      "time": "08:00",
      "room": "Lab Komputer 1",
      "status": "OK"
    }
  ],
  "statistics": {
    "fitness": 0.9542,
    "executionTime": 12.34,
    "generations": 25,
    "totalViolations": 2,
    "reservedViolations": 0,
    "ramUsage": 156
  },
  "success": true
}
```

## 🎨 Customization

### Styling
```css
/* Custom color scheme */
:root {
    --primary-color: #your-primary-color;
    --secondary-color: #your-secondary-color;
    --success-color: #your-success-color;
}

/* Custom animations */
.custom-animation {
    animation: yourAnimation 1s ease-in-out;
}
```

### JavaScript Extensions
```javascript
// Extend the SchedulingInterface class
class CustomSchedulingInterface extends SchedulingInterface {
    constructor() {
        super();
        this.setupCustomFeatures();
    }
    
    setupCustomFeatures() {
        // Add your custom functionality
    }
}
```

## 🐛 Troubleshooting

### Common Issues

#### File Upload Errors
```
Error: "File too large"
Solution: Increase MAX_CONTENT_LENGTH in configuration
```

#### Processing Timeout
```
Error: "Scheduling timeout or failed"
Solution: Reduce population size or max generations
```

#### Memory Issues
```
Error: "Out of memory"
Solution: Reduce dataset size or increase server memory
```

#### Invalid File Format
```
Error: "Missing required columns"
Solution: Check CSV/Excel file structure matches requirements
```

### Debug Mode
```bash
# Enable detailed logging
export FLASK_DEBUG=1
python run.py --mode dev
```

### Performance Monitoring
```python
# Add to app.py for performance tracking
import time
from functools import wraps

def monitor_performance(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        end_time = time.time()
        print(f"{f.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return decorated_function
```

## 📈 Performance Optimization

### Frontend
- **Lazy Loading**: Load components as needed
- **File Chunking**: Process large files in chunks
- **Caching**: Cache processed results
- **Compression**: Gzip static assets

### Backend
- **Database Connection Pooling**: For production databases
- **Redis Caching**: Cache frequent operations
- **Celery Task Queue**: Handle long-running jobs
- **Load Balancing**: Multiple worker processes

## 🔒 Security

### File Upload Security
- File type validation
- File size limits  
- Virus scanning (production)
- Sandboxed processing

### General Security
- CSRF protection with Flask-WTF
- Input validation and sanitization
- Rate limiting for API endpoints
- Secure headers configuration

## 📞 Support

### Development Help
1. Check browser console for JavaScript errors
2. Check Flask logs for backend errors
3. Verify file formats match requirements
4. Test with smaller datasets first

### Production Issues
1. Check Gunicorn/Nginx logs
2. Monitor memory and CPU usage
3. Verify environment variables
4. Test file permissions on upload directory

---

**Built with ❤️ for Educational Excellence** 🎓