#!/usr/bin/env python3

from flask import Flask, jsonify, request, render_template_string, send_from_directory
from flask_cors import CORS
from dbConfig import GetAllDB, get_kuliah_with_dosen_info, db, get_schedule_data
from scheduler_wrapper import UniversityScheduler
from parameter_optimizer import ParameterOptimizer
import json
import os
import threading
import time

app = Flask(__name__)
CORS(app)

# Configure Flask
app.config['JSON_SORT_KEYS'] = False

# Global variables for schedule generation
current_schedule_task = None
schedule_progress = {'status': 'idle', 'progress': 0, 'message': ''}
generated_schedule = None

@app.route('/')
def index():
    """Serve the main HTML page"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        return "index.html not found", 404

@app.route('/api/data')
def get_all_data():
    """Get all data needed for the frontend"""
    try:
        # Get all basic data
        dosen_data = GetAllDB('dosen')
        kuliah_data = get_kuliah_with_dosen_info()
        waktu_data = GetAllDB('waktu')
        ruangan_data = GetAllDB('ruangan')
        
        # Get preferences data
        preferences_data = get_preferences_with_details()
        
        return jsonify({
            'dosen': dosen_data,
            'kuliah': kuliah_data,
            'waktu': waktu_data,
            'ruangan': ruangan_data,
            'preferences': preferences_data
        })
    except Exception as e:
        print(f"Error getting data: {e}")
        return jsonify({'error': str(e)}), 500

def get_preferences_with_details():
    """Get preferences data with waktu details"""
    if not db.connect():
        return []
    
    try:
        cursor = db.connection.cursor(dictionary=True)
        
        # Query to get preferences with waktu details
        query = """
        SELECT r.id, r.nidn, r.nama_dosen, r.hari, 
               r.waktu_suka, r.waktu_tidak_bisa,
               r.created_at, r.updated_at
        FROM referensi_waktu_dosen r
        ORDER BY r.nama_dosen, r.hari
        """
        
        cursor.execute(query)
        preferences = cursor.fetchall()
        
        # Process each preference to add waktu details
        for pref in preferences:
            # Parse JSON arrays
            try:
                waktu_suka_ids = json.loads(pref['waktu_suka']) if pref['waktu_suka'] else []
                waktu_tidak_bisa_ids = json.loads(pref['waktu_tidak_bisa']) if pref['waktu_tidak_bisa'] else []
            except:
                waktu_suka_ids = []
                waktu_tidak_bisa_ids = []
            
            # Get waktu details
            pref['waktu_suka_detail'] = get_waktu_by_ids(waktu_suka_ids)
            pref['waktu_tidak_bisa_detail'] = get_waktu_by_ids(waktu_tidak_bisa_ids)
        
        cursor.close()
        return preferences
        
    except Exception as e:
        print(f"Error getting preferences: {e}")
        return []
    
    finally:
        db.disconnect()

def get_waktu_by_ids(waktu_ids):
    """Get waktu details by IDs"""
    if not waktu_ids:
        return []
    
    if not db.connection or not db.connection.is_connected():
        if not db.connect():
            return []
    
    try:
        cursor = db.connection.cursor(dictionary=True)
        
        # Create placeholder string for IN clause
        placeholders = ','.join(['%s'] * len(waktu_ids))
        query = f"SELECT waktu FROM waktu WHERE kode_waktu IN ({placeholders}) ORDER BY kode_waktu"
        
        cursor.execute(query, waktu_ids)
        results = cursor.fetchall()
        cursor.close()
        
        return [result['waktu'] for result in results]
        
    except Exception as e:
        print(f"Error getting waktu by IDs: {e}")
        return []

@app.route('/api/preferences', methods=['POST'])
def add_preference():
    """Add new dosen preference"""
    try:
        data = request.get_json()
        
        if not data or not data.get('nidn') or not data.get('hari'):
            return jsonify({'error': 'NIDN and hari are required'}), 400
        
        # Get dosen name
        dosen_data = GetAllDB('dosen')
        dosen_name = None
        for dosen in dosen_data:
            if dosen['nidn'] == data['nidn']:
                dosen_name = dosen['nama']
                break
        
        if not dosen_name:
            return jsonify({'error': 'Dosen not found'}), 404
        
        if not db.connect():
            return jsonify({'error': 'Database connection failed'}), 500
        
        try:
            cursor = db.connection.cursor()
            
            # Convert arrays to JSON strings
            waktu_suka = json.dumps(data.get('waktu_suka', []))
            waktu_tidak_bisa = json.dumps(data.get('waktu_tidak_bisa', []))
            
            # Insert or update preference
            insert_sql = """
            INSERT INTO referensi_waktu_dosen 
            (nidn, nama_dosen, hari, waktu_suka, waktu_tidak_bisa) 
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            waktu_suka = VALUES(waktu_suka),
            waktu_tidak_bisa = VALUES(waktu_tidak_bisa),
            updated_at = CURRENT_TIMESTAMP
            """
            
            cursor.execute(insert_sql, (
                data['nidn'],
                dosen_name,
                data['hari'],
                waktu_suka,
                waktu_tidak_bisa
            ))
            
            db.connection.commit()
            cursor.close()
            
            return jsonify({'message': 'Preference added successfully'})
            
        except Exception as e:
            if db.connection:
                db.connection.rollback()
            return jsonify({'error': f'Database error: {str(e)}'}), 500
        
        finally:
            db.disconnect()
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/preferences/<int:pref_id>', methods=['DELETE'])
def delete_preference(pref_id):
    """Delete a preference"""
    try:
        if not db.connect():
            return jsonify({'error': 'Database connection failed'}), 500
        
        try:
            cursor = db.connection.cursor()
            
            # Delete preference
            delete_sql = "DELETE FROM referensi_waktu_dosen WHERE id = %s"
            cursor.execute(delete_sql, (pref_id,))
            
            if cursor.rowcount == 0:
                return jsonify({'error': 'Preference not found'}), 404
            
            db.connection.commit()
            cursor.close()
            
            return jsonify({'message': 'Preference deleted successfully'})
            
        except Exception as e:
            if db.connection:
                db.connection.rollback()
            return jsonify({'error': f'Database error: {str(e)}'}), 500
        
        finally:
            db.disconnect()
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/waktu/by-day/<day>')
def get_waktu_by_day(day):
    """Get waktu slots for a specific day"""
    try:
        waktu_data = GetAllDB('waktu')
        day_waktu = [w for w in waktu_data if w['nama_hari'] == day.upper()]
        return jsonify(day_waktu)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.route('/api/generate-schedule', methods=['POST'])
def generate_schedule():
    """Generate schedule using genetic algorithm"""
    global current_schedule_task, schedule_progress, generated_schedule
    
    try:
        data = request.get_json() or {}
        
        # Check if already generating
        if schedule_progress['status'] == 'generating':
            return jsonify({'error': 'Schedule generation already in progress'}), 400
        
        # Initialize scheduler
        scheduler = UniversityScheduler()
        
        # Update parameters if provided
        if 'population_size' in data:
            scheduler.population_size = max(4, min(20, data['population_size']))
        if 'max_generations' in data:
            scheduler.max_generations = max(10, min(500, data['max_generations']))
        if 'crossover_rate' in data:
            scheduler.crossover_rate = max(0.1, min(1.0, data['crossover_rate']))
        if 'mutation_rate' in data:
            scheduler.mutation_rate = max(0.01, min(0.5, data['mutation_rate']))
        
        def progress_callback(progress_data):
            """Update progress during generation"""
            global schedule_progress
            schedule_progress.update({
                'status': 'generating',
                'progress': progress_data['progress'],
                'generation': progress_data['generation'],
                'max_generations': progress_data['max_generations'],
                'best_fitness': progress_data['best_fitness'],
                'avg_fitness': progress_data['avg_fitness'],
                'message': f"Generation {progress_data['generation']}/{progress_data['max_generations']}"
            })
        
        def generate_async():
            """Run schedule generation in background"""
            global schedule_progress, generated_schedule
            try:
                schedule_progress.update({
                    'status': 'generating',
                    'progress': 0,
                    'message': 'Initializing genetic algorithm...'
                })
                
                result = scheduler.generate_schedule(progress_callback)
                
                if result['success']:
                    generated_schedule = result
                    schedule_progress.update({
                        'status': 'completed',
                        'progress': 100,
                        'message': 'Schedule generation completed successfully!'
                    })
                else:
                    schedule_progress.update({
                        'status': 'error',
                        'progress': 0,
                        'message': 'Schedule generation failed'
                    })
                    
            except Exception as e:
                schedule_progress.update({
                    'status': 'error',
                    'progress': 0,
                    'message': f'Error: {str(e)}'
                })
        
        # Start generation in background thread
        current_schedule_task = threading.Thread(target=generate_async)
        current_schedule_task.daemon = True
        current_schedule_task.start()
        
        return jsonify({
            'message': 'Schedule generation started',
            'status': 'generating'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to start schedule generation: {str(e)}'}), 500

@app.route('/api/schedule-progress')
def get_schedule_progress():
    """Get current progress of schedule generation"""
    global schedule_progress
    return jsonify(schedule_progress)

@app.route('/api/generated-schedule')
def get_generated_schedule():
    """Get the generated schedule"""
    global generated_schedule
    
    if not generated_schedule:
        return jsonify({'error': 'No schedule has been generated yet'}), 404
    
    return jsonify(generated_schedule)

@app.route('/api/cancel-generation', methods=['POST'])
def cancel_generation():
    """Cancel current schedule generation"""
    global schedule_progress, current_schedule_task
    
    if schedule_progress['status'] == 'generating':
        schedule_progress.update({
            'status': 'cancelled',
            'progress': 0,
            'message': 'Schedule generation cancelled'
        })
        # Note: Thread cancellation is limited in Python, but we set status to cancelled
        return jsonify({'message': 'Schedule generation cancelled'})
    
    return jsonify({'message': 'No active generation to cancel'})

@app.route('/api/parameter-recommendations')
def get_parameter_recommendations():
    """Get optimal parameter recommendations based on data"""
    try:
        # Get current data
        data = get_schedule_data()
        
        # Create optimizer and get recommendations
        optimizer = ParameterOptimizer(data)
        recommendations = optimizer.get_parameter_recommendations()
        
        return jsonify(recommendations)
        
    except Exception as e:
        print(f"Error getting parameter recommendations: {e}")
        return jsonify({'error': f'Failed to get recommendations: {str(e)}'}), 500

@app.route('/api/analyze-complexity')
def analyze_complexity():
    """Analyze problem complexity"""
    try:
        # Get current data
        data = get_schedule_data()
        
        # Create optimizer and analyze
        optimizer = ParameterOptimizer(data)
        analysis = optimizer.analyze_problem_complexity()
        
        return jsonify(analysis)
        
    except Exception as e:
        print(f"Error analyzing complexity: {e}")
        return jsonify({'error': f'Failed to analyze complexity: {str(e)}'}), 500

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting Enhanced University Scheduling System...")
    print("📊 Loading database data...")
    
    try:
        # Test database connection
        if db.connect():
            print("✓ Database connected successfully")
            db.disconnect()
        else:
            print("✗ Database connection failed")
    except Exception as e:
        print(f"✗ Database error: {e}")
    
    print("🌐 Starting web server...")
    print("💫 Access the Gen Z Dashboard at: http://localhost:5000")
    print("✨ Features available:")
    print("   - Modern dashboard with statistics")
    print("   - View dosen, kuliah, waktu, ruangan data")
    print("   - Add/manage dosen preferences")
    print("   - 50-minute interval time system")
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=True)