#!/usr/bin/env python3
"""
Enhanced University Scheduling System - Flask Web Application
Provides web interface for CSV/Excel upload and scheduling optimization
"""

import os
import io
import json
import time
import pandas as pd
import numpy as np
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, Response
from werkzeug.utils import secure_filename
import threading
import queue
from typing import Dict, List, Any, Optional

# Import our enhanced scheduling system
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from enhanced_scheduler import EnhancedScheduler

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class SchedulingWebService:
    def __init__(self):
        self.current_jobs = {}
        self.job_counter = 0
    
    def validate_file(self, file) -> tuple[bool, str]:
        """Validate uploaded file"""
        if not file:
            return False, "No file provided"
        
        if file.filename == '':
            return False, "No file selected"
        
        # Check file extension
        allowed_extensions = {'.csv', '.xlsx', '.xls'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return False, f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        
        # Check file size (already handled by Flask config, but double-check)
        file.seek(0, 2)  # Go to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > app.config['MAX_CONTENT_LENGTH']:
            return False, "File too large. Maximum size: 16MB"
        
        return True, "File valid"
    
    def read_file_data(self, file) -> tuple[bool, pd.DataFrame, str]:
        """Read data from uploaded file"""
        try:
            file_ext = os.path.splitext(file.filename)[1].lower()
            
            if file_ext == '.csv':
                # Try different encodings for CSV
                try:
                    df = pd.read_csv(file, encoding='utf-8')
                except UnicodeDecodeError:
                    file.seek(0)
                    try:
                        df = pd.read_csv(file, encoding='latin-1')
                    except UnicodeDecodeError:
                        file.seek(0)
                        df = pd.read_csv(file, encoding='cp1252')
            
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file, engine='openpyxl' if file_ext == '.xlsx' else 'xlrd')
            
            else:
                return False, None, "Unsupported file format"
            
            # Clean column names
            df.columns = df.columns.str.strip().str.lower()
            
            # Remove empty rows
            df = df.dropna(how='all')
            
            return True, df, "File read successfully"
        
        except Exception as e:
            return False, None, f"Error reading file: {str(e)}"
    
    def validate_data_structure(self, df: pd.DataFrame, data_type: str) -> tuple[bool, str]:
        """Validate data structure based on type"""
        required_columns = {
            'courses': ['nama', 'dosen', 'sks'],
            'times': ['hari', 'jam_mulai'],
            'rooms': ['nama', 'kapasitas'],
            'preferences': ['dosen']  # Optional file
        }
        
        if data_type not in required_columns:
            return False, f"Unknown data type: {data_type}"
        
        required = required_columns[data_type]
        missing = [col for col in required if col not in df.columns]
        
        if missing and data_type != 'preferences':
            return False, f"Missing required columns: {', '.join(missing)}"
        
        # Additional validation
        if data_type == 'courses':
            # Check if SKS column contains numeric values
            try:
                df['sks'] = pd.to_numeric(df['sks'], errors='coerce')
                if df['sks'].isna().any():
                    return False, "SKS column must contain numeric values"
            except Exception:
                return False, "Invalid SKS data format"
        
        elif data_type == 'rooms':
            # Check if capacity column contains numeric values
            try:
                df['kapasitas'] = pd.to_numeric(df['kapasitas'], errors='coerce')
                if df['kapasitas'].isna().any():
                    return False, "Kapasitas column must contain numeric values"
            except Exception:
                return False, "Invalid kapasitas data format"
        
        elif data_type == 'times':
            # Validate time format
            time_pattern = r'^\\d{2}:\\d{2}$'
            if not df['jam_mulai'].str.match(time_pattern).all():
                return False, "jam_mulai must be in HH:MM format"
        
        return True, f"{data_type.title()} data validated successfully"
    
    def convert_to_scheduler_format(self, data_dict: Dict[str, pd.DataFrame]) -> Dict[str, List]:
        """Convert pandas DataFrames to format expected by scheduler"""
        converted = {}
        
        # Convert courses
        if 'courses' in data_dict:
            df = data_dict['courses']
            converted['kuliah'] = []
            for idx, row in df.iterrows():
                converted['kuliah'].append({
                    'id': idx,
                    'nama': str(row['nama']),
                    'dosen': str(row['dosen']),
                    'sks': int(row['sks'])
                })
        
        # Convert times
        if 'times' in data_dict:
            df = data_dict['times']
            converted['waktu'] = []
            for idx, row in df.iterrows():
                converted['waktu'].append([
                    idx,
                    str(row['hari']),
                    str(row['jam_mulai'])
                ])
        
        # Convert rooms
        if 'rooms' in data_dict:
            df = data_dict['rooms']
            converted['ruangan'] = []
            for idx, row in df.iterrows():
                converted['ruangan'].append([
                    idx,
                    str(row['nama']),
                    int(row['kapasitas'])
                ])
        
        # Convert preferences if available
        if 'preferences' in data_dict:
            df = data_dict['preferences']
            converted['preferensi_dosen'] = []
            for _, row in df.iterrows():
                pref_waktu = []
                tidak_bisa = []
                
                # Parse preference columns if they exist
                if 'preferensi_waktu' in df.columns and pd.notna(row['preferensi_waktu']):
                    try:
                        pref_waktu = json.loads(str(row['preferensi_waktu']))
                    except (json.JSONDecodeError, ValueError):
                        # Try to parse as comma-separated values
                        pref_waktu = [int(x.strip()) for x in str(row['preferensi_waktu']).split(',') if x.strip().isdigit()]
                
                if 'tidak_bisa_waktu' in df.columns and pd.notna(row['tidak_bisa_waktu']):
                    try:
                        tidak_bisa = json.loads(str(row['tidak_bisa_waktu']))
                    except (json.JSONDecodeError, ValueError):
                        # Try to parse as comma-separated values
                        tidak_bisa = [int(x.strip()) for x in str(row['tidak_bisa_waktu']).split(',') if x.strip().isdigit()]
                
                converted['preferensi_dosen'].append({
                    'dosen': str(row['dosen']),
                    'preferensi_waktu': pref_waktu,
                    'tidak_bisa_waktu': tidak_bisa
                })
        
        return converted
    
    def run_scheduling(self, job_id: str, data: Dict, config: Dict, progress_queue: queue.Queue):
        """Run scheduling in background thread"""
        try:
            progress_queue.put({
                'type': 'progress',
                'progress': 10,
                'message': 'Initializing scheduler...'
            })
            
            # Initialize enhanced scheduler
            scheduler = EnhancedScheduler(data, config)
            
            progress_queue.put({
                'type': 'progress', 
                'progress': 20,
                'message': 'Pre-allocating reserved slots...'
            })
            
            # Run scheduling with progress updates
            def progress_callback(generation, fitness, message):
                progress = 20 + (generation / config['algorithm']['maxGenerations']) * 60
                progress_queue.put({
                    'type': 'generation',
                    'generation': generation,
                    'fitness': fitness,
                    'progress': progress,
                    'message': message
                })
            
            result = scheduler.optimize(progress_callback)
            
            progress_queue.put({
                'type': 'progress',
                'progress': 90,
                'message': 'Formatting results...'
            })
            
            # Format results for web display
            formatted_result = self.format_results(result, data)
            
            progress_queue.put({
                'type': 'complete',
                'result': formatted_result
            })
            
        except Exception as e:
            progress_queue.put({
                'type': 'error',
                'message': str(e)
            })
    
    def format_results(self, raw_results: Dict, original_data: Dict) -> Dict:
        """Format scheduling results for web display"""
        try:
            schedule = []
            statistics = raw_results.get('statistics', {})
            best_schedule = raw_results.get('best_schedule', {})
            
            # Convert schedule to displayable format
            for gene_idx, gene in best_schedule.items():
                course_info = original_data['kuliah'][gene['kuliah']]
                time_info = original_data['waktu'][gene['waktu']]
                room_info = original_data['ruangan'][gene['ruang']]
                
                # Determine status based on violations
                status = 'OK'
                violations = raw_results.get('violations', {})
                
                if gene_idx in violations.get('reserved_violations', []):
                    status = 'Reserved Violation'
                elif gene_idx in violations.get('preference_violations', []):
                    status = 'Preference Issue'
                elif gene_idx in violations.get('clashes', []):
                    status = 'Clash'
                
                schedule.append({
                    'course': course_info['nama'],
                    'lecturer': course_info['dosen'],
                    'sks': course_info['sks'],
                    'day': time_info[1],
                    'time': time_info[2],
                    'room': room_info[1],
                    'capacity': room_info[2],
                    'status': status
                })
            
            # Format statistics
            formatted_stats = {
                'fitness': statistics.get('best_fitness', 0.0),
                'executionTime': statistics.get('execution_time', 0.0),
                'generations': statistics.get('generations_completed', 0),
                'totalViolations': statistics.get('total_violations', 0),
                'reservedViolations': statistics.get('reserved_violations', 0),
                'preferenceViolations': statistics.get('preference_violations', 0),
                'clashes': statistics.get('clashes', 0),
                'ramUsage': statistics.get('ram_usage_mb', 0)
            }
            
            return {
                'schedule': schedule,
                'statistics': formatted_stats,
                'success': statistics.get('success_achieved', False),
                'message': 'Scheduling optimization completed successfully'
            }
            
        except Exception as e:
            return {
                'schedule': [],
                'statistics': {},
                'success': False,
                'message': f"Error formatting results: {str(e)}"
            }

# Initialize service
service = SchedulingWebService()

@app.route('/')
def index():
    """Main page with file upload interface"""
    return render_template('index.html')

@app.route('/api/schedule', methods=['POST'])
def schedule():
    """Handle scheduling request with file uploads"""
    try:
        # Validate request
        if not any(key in request.files for key in ['courses', 'times', 'rooms']):
            return jsonify({'error': 'Missing required files'}), 400
        
        # Process uploaded files
        data_dict = {}
        file_info = {}
        
        for file_type in ['courses', 'times', 'rooms', 'preferences']:
            if file_type in request.files:
                file = request.files[file_type]
                
                # Validate file
                valid, message = service.validate_file(file)
                if not valid:
                    return jsonify({'error': f'{file_type}: {message}'}), 400
                
                # Read file data
                success, df, message = service.read_file_data(file)
                if not success:
                    return jsonify({'error': f'{file_type}: {message}'}), 400
                
                # Validate data structure
                valid, message = service.validate_data_structure(df, file_type)
                if not valid:
                    return jsonify({'error': f'{file_type}: {message}'}), 400
                
                data_dict[file_type] = df
                file_info[file_type] = {
                    'filename': file.filename,
                    'rows': len(df),
                    'columns': list(df.columns)
                }
        
        # Parse configuration
        try:
            config = json.loads(request.form.get('config', '{}'))
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid configuration JSON'}), 400
        
        # Convert data to scheduler format
        scheduler_data = service.convert_to_scheduler_format(data_dict)
        
        # For synchronous response (simple version)
        if request.headers.get('Accept') == 'application/json':
            # Run scheduling synchronously
            job_id = f"job_{service.job_counter}"
            service.job_counter += 1
            
            progress_queue = queue.Queue()
            
            # Run in thread but wait for completion
            thread = threading.Thread(
                target=service.run_scheduling,
                args=(job_id, scheduler_data, config, progress_queue)
            )
            thread.start()
            thread.join(timeout=300)  # 5 minute timeout
            
            # Get final result
            final_result = None
            while not progress_queue.empty():
                update = progress_queue.get()
                if update['type'] == 'complete':
                    final_result = update['result']
                elif update['type'] == 'error':
                    return jsonify({'error': update['message']}), 500
            
            if final_result:
                return jsonify(final_result)
            else:
                return jsonify({'error': 'Scheduling timeout or failed'}), 500
        
        # For streaming response (Server-Sent Events)
        else:
            def generate_progress():
                job_id = f"job_{service.job_counter}"
                service.job_counter += 1
                
                progress_queue = queue.Queue()
                
                # Start background thread
                thread = threading.Thread(
                    target=service.run_scheduling,
                    args=(job_id, scheduler_data, config, progress_queue)
                )
                thread.start()
                
                # Stream progress updates
                while thread.is_alive() or not progress_queue.empty():
                    try:
                        update = progress_queue.get(timeout=1.0)
                        yield f"data: {json.dumps(update)}\\n\\n"
                        
                        if update['type'] in ['complete', 'error']:
                            break
                    except queue.Empty:
                        continue
                
                thread.join()
            
            return Response(
                generate_progress(),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive'
                }
            )
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/export/<format>', methods=['POST'])
def export_schedule(format):
    """Export schedule in various formats"""
    try:
        data = request.get_json()
        if not data or 'schedule' not in data:
            return jsonify({'error': 'No schedule data provided'}), 400
        
        schedule_df = pd.DataFrame(data['schedule'])
        
        if format.lower() == 'excel':
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                schedule_df.to_excel(writer, sheet_name='Schedule', index=False)
                
                # Add statistics sheet if available
                if 'statistics' in data:
                    stats_df = pd.DataFrame([data['statistics']])
                    stats_df.to_excel(writer, sheet_name='Statistics', index=False)
            
            output.seek(0)
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'schedule_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            )
        
        elif format.lower() == 'csv':
            output = io.StringIO()
            schedule_df.to_csv(output, index=False)
            output.seek(0)
            
            response = Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename=schedule_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
            )
            return response
        
        else:
            return jsonify({'error': f'Unsupported export format: {format}'}), 400
    
    except Exception as e:
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

@app.route('/api/report', methods=['POST'])
def generate_report():
    """Generate detailed PDF report"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # For now, return a simple text report
        # In production, you'd use a library like reportlab to generate PDFs
        
        report_content = f"""
ENHANCED SCHEDULING SYSTEM - OPTIMIZATION REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

STATISTICS:
- Best Fitness: {data.get('results', {}).get('statistics', {}).get('fitness', 'N/A')}
- Execution Time: {data.get('results', {}).get('statistics', {}).get('executionTime', 'N/A')}s
- Generations: {data.get('results', {}).get('statistics', {}).get('generations', 'N/A')}
- Total Violations: {data.get('results', {}).get('statistics', {}).get('totalViolations', 'N/A')}

CONFIGURATION:
{json.dumps(data.get('config', {}), indent=2)}

SCHEDULE:
"""
        
        schedule = data.get('results', {}).get('schedule', [])
        for item in schedule:
            report_content += f"- {item.get('course', 'N/A')} | {item.get('lecturer', 'N/A')} | {item.get('day', 'N/A')} {item.get('time', 'N/A')} | {item.get('room', 'N/A')} | Status: {item.get('status', 'N/A')}\\n"
        
        output = io.BytesIO(report_content.encode('utf-8'))
        output.seek(0)
        
        return send_file(
            output,
            mimetype='text/plain',
            as_attachment=True,
            download_name=f'scheduling_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        )
    
    except Exception as e:
        return jsonify({'error': f'Report generation failed: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    })

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'File too large. Maximum size: 16MB'}), 413

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🎓 Enhanced University Scheduling System")
    print("🌐 Starting web server...")
    print("📁 Upload folder:", app.config['UPLOAD_FOLDER'])
    print("📊 Max file size:", app.config['MAX_CONTENT_LENGTH'] / (1024*1024), "MB")
    
    # Development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )