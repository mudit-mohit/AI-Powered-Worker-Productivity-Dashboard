from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime, timedelta
import random
import os

# Serve frontend build files
app = Flask(__name__, static_folder='../frontend/build', static_url_path='')
CORS(app)

# Database initialization
DATABASE = 'factory.db'

# Serve index.html for React routing
@app.route('/')
def serve_index():
    """Serve the frontend index.html"""
    index_path = os.path.join(app.static_folder, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(app.static_folder, 'index.html')
    return jsonify({'message': 'Frontend not built. Run npm run build in frontend directory.'}), 404

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files (CSS, JS, images, etc.)"""
    file_path = os.path.join(app.static_folder, path)
    if os.path.isfile(file_path):
        return send_from_directory(app.static_folder, path)
    # For any non-existent routes, serve index.html for React routing
    index_path = os.path.join(app.static_folder, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(app.static_folder, 'index.html')
    return jsonify({'error': 'Not found'}), 404

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with schema and sample data"""
    if os.path.exists(DATABASE):
        return
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE workers (
            worker_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            email TEXT UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE workstations (
            station_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            type TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id INTEGER NOT NULL,
            station_id INTEGER NOT NULL,
            event_type TEXT NOT NULL CHECK(event_type IN ('working', 'idle', 'absent', 'product_count')),
            timestamp DATETIME NOT NULL,
            duration INTEGER,
            confidence REAL,
            count INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (worker_id) REFERENCES workers(worker_id),
            FOREIGN KEY (station_id) REFERENCES workstations(station_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE productivity_metrics (
            metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id INTEGER NOT NULL,
            date DATE,
            active_time INTEGER DEFAULT 0,
            idle_time INTEGER DEFAULT 0,
            productivity_score REAL DEFAULT 0.0,
            product_count INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (worker_id) REFERENCES workers(worker_id),
            UNIQUE(worker_id, date)
        )
    ''')
    
    # Create indices for better query performance
    cursor.execute('CREATE INDEX idx_events_worker_id ON events(worker_id)')
    cursor.execute('CREATE INDEX idx_events_station_id ON events(station_id)')
    cursor.execute('CREATE INDEX idx_events_timestamp ON events(timestamp)')
    cursor.execute('CREATE INDEX idx_metrics_worker_id ON productivity_metrics(worker_id)')
    cursor.execute('CREATE INDEX idx_metrics_date ON productivity_metrics(date)')
    
    # Seed initial data
    seed_initial_data(cursor)
    
    conn.commit()
    conn.close()
    print("✓ Database initialized with sample data")

# ===== METRICS COMPUTATION FUNCTIONS =====
# Assumptions Documentation:
# - Default event duration: 300 seconds if not specified
# - Working shift: 8 AM - 6 PM
# - Active time = duration of 'working' + 'product_count' events
# - Idle time = duration of 'idle' events
# - Utilization = active_time / (active_time + idle_time)
# - Production = sum of 'count' field from 'product_count' events
# - Units per hour = total production / total active time in hours
# - Workstation occupancy = sum of all worker event durations at that station
# - Throughput rate = units per hour at workstation level

DEFAULT_EVENT_DURATION = 300  
SHIFT_START_HOUR = 8
SHIFT_END_HOUR = 18
SHIFT_DURATION = (SHIFT_END_HOUR - SHIFT_START_HOUR) * 3600  

def calculate_worker_metrics(worker_id, date_from=None, date_to=None):
    """
    Calculate comprehensive worker-level metrics
    
    Args:
        worker_id: ID of the worker
        date_from: Start date (format: YYYY-MM-DD), defaults to 7 days ago
        date_to: End date (format: YYYY-MM-DD), defaults to today
    
    Returns:
        Dictionary with worker metrics
    """
    if not date_from:
        date_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    if not date_to:
        date_to = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all events for worker in date range
    cursor.execute('''
        SELECT event_type, duration, count, timestamp
        FROM events
        WHERE worker_id = ? AND DATE(timestamp) BETWEEN ? AND ?
        ORDER BY timestamp
    ''', (worker_id, date_from, date_to))
    
    events = cursor.fetchall()
    
    # Get worker info
    cursor.execute('SELECT * FROM workers WHERE worker_id = ?', (worker_id,))
    worker_row = cursor.fetchone()
    worker = dict(worker_row) if worker_row else None
    
    conn.close()
    
    # Initialize metrics
    active_time = 0  
    idle_time = 0    
    absent_time = 0  
    total_units = 0
    working_events = 0
    idle_events = 0
    product_events = 0
    event_count = 0
    
    # Process events
    for event in events:
        event_type = event['event_type']
        duration = event['duration'] if event['duration'] else DEFAULT_EVENT_DURATION
        count = event['count'] if event['count'] else 0
        
        event_count += 1
        
        if event_type == 'working':
            active_time += duration
            working_events += 1
        elif event_type == 'product_count':
            active_time += duration
            total_units += count
            product_events += 1
        elif event_type == 'idle':
            idle_time += duration
            idle_events += 1
        elif event_type == 'absent':
            absent_time += duration
    
    # Calculate utilization
    total_tracked_time = active_time + idle_time
    utilization_pct = (active_time / total_tracked_time * 100) if total_tracked_time > 0 else 0
    
    # Calculate units per hour
    active_hours = active_time / 3600
    units_per_hour = (total_units / active_hours) if active_hours > 0 else 0
    
    # Calculate units per shift
    units_per_shift = (total_units * SHIFT_DURATION / active_time) if active_time > 0 else 0
    
    return {
        'worker_id': worker_id,
        'worker_name': worker['name'] if worker else 'Unknown',
        'date_range': {
            'from': date_from,
            'to': date_to
        },
        'active_time_seconds': active_time,
        'active_time_hours': round(active_hours, 2),
        'idle_time_seconds': idle_time,
        'idle_time_hours': round(idle_time / 3600, 2),
        'absent_time_seconds': absent_time,
        'absent_time_hours': round(absent_time / 3600, 2),
        'total_tracked_time_seconds': total_tracked_time,
        'utilization_percentage': round(utilization_pct, 2),
        'total_units_produced': total_units,
        'units_per_hour': round(units_per_hour, 2),
        'units_per_shift': round(units_per_shift, 2),
        'event_breakdown': {
            'working_events': working_events,
            'product_events': product_events,
            'idle_events': idle_events,
            'total_events': event_count
        }
    }

def calculate_workstation_metrics(station_id, date_from=None, date_to=None):
    """
    Calculate comprehensive workstation-level metrics
    
    Args:
        station_id: ID of the workstation
        date_from: Start date, defaults to 7 days ago
        date_to: End date, defaults to today
    
    Returns:
        Dictionary with workstation metrics
    """
    if not date_from:
        date_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    if not date_to:
        date_to = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all events at this workstation in date range
    cursor.execute('''
        SELECT event_type, duration, count, timestamp
        FROM events
        WHERE station_id = ? AND DATE(timestamp) BETWEEN ? AND ?
        ORDER BY timestamp
    ''', (station_id, date_from, date_to))
    
    events = cursor.fetchall()
    
    # Get workstation info
    cursor.execute('SELECT * FROM workstations WHERE station_id = ?', (station_id,))
    station_row = cursor.fetchone()
    station = dict(station_row) if station_row else None
    
    # Get unique workers who used this station
    cursor.execute('''
        SELECT DISTINCT worker_id FROM events
        WHERE station_id = ? AND DATE(timestamp) BETWEEN ? AND ?
    ''', (station_id, date_from, date_to))
    
    worker_ids = [row['worker_id'] for row in cursor.fetchall()]
    
    conn.close()
    
    # Initialize metrics
    occupancy_time = 0  
    productive_time = 0  
    idle_time = 0
    total_units = 0
    unique_dates = set()
    
    # Process events
    for event in events:
        event_type = event['event_type']
        duration = event['duration'] if event['duration'] else DEFAULT_EVENT_DURATION
        count = event['count'] if event['count'] else 0
        timestamp = event['timestamp']
        
        # Track unique dates for occupancy calculation
        date = timestamp.split('T')[0]
        unique_dates.add(date)
        
        if event_type in ['working', 'product_count']:
            productive_time += duration
            occupancy_time += duration
            if event_type == 'product_count':
                total_units += count
        elif event_type == 'idle':
            occupancy_time += duration
            idle_time += duration
    
    # Calculate utilization
    utilization_pct = (productive_time / occupancy_time * 100) if occupancy_time > 0 else 0
    
    # Calculate throughput
    productive_hours = productive_time / 3600
    throughput_rate = (total_units / productive_hours) if productive_hours > 0 else 0
    
    # Calculate average units per day
    days_count = len(unique_dates) if unique_dates else 1
    units_per_day = total_units / days_count
    
    return {
        'station_id': station_id,
        'station_name': station['name'] if station else 'Unknown',
        'station_type': station['type'] if station else 'Unknown',
        'date_range': {
            'from': date_from,
            'to': date_to
        },
        'occupancy_time_seconds': occupancy_time,
        'occupancy_time_hours': round(occupancy_time / 3600, 2),
        'productive_time_seconds': productive_time,
        'productive_time_hours': round(productive_time / 3600, 2),
        'idle_time_seconds': idle_time,
        'idle_time_hours': round(idle_time / 3600, 2),
        'utilization_percentage': round(utilization_pct, 2),
        'total_units_produced': total_units,
        'throughput_rate_units_per_hour': round(throughput_rate, 2),
        'units_per_day': round(units_per_day, 2),
        'unique_workers': len(worker_ids),
        'days_active': days_count
    }

def calculate_factory_metrics(date_from=None, date_to=None):
    """
    Calculate comprehensive factory-level metrics across all workers and workstations
    
    Args:
        date_from: Start date, defaults to 7 days ago
        date_to: End date, defaults to today
    
    Returns:
        Dictionary with factory-wide metrics
    """
    if not date_from:
        date_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    if not date_to:
        date_to = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all events in date range
    cursor.execute('''
        SELECT event_type, duration, count
        FROM events
        WHERE DATE(timestamp) BETWEEN ? AND ?
    ''', (date_from, date_to))
    
    events = cursor.fetchall()
    
    # Get all workers
    cursor.execute('SELECT COUNT(*) as count FROM workers')
    total_workers = dict(cursor.fetchone())['count']
    
    # Get all workstations
    cursor.execute('SELECT COUNT(*) as count FROM workstations')
    total_stations = dict(cursor.fetchone())['count']
    
    # Get unique workers with events
    cursor.execute('''
        SELECT DISTINCT worker_id FROM events
        WHERE DATE(timestamp) BETWEEN ? AND ?
    ''', (date_from, date_to))
    
    active_workers = len(cursor.fetchall())
    
    # Get unique workstations with events
    cursor.execute('''
        SELECT DISTINCT station_id FROM events
        WHERE DATE(timestamp) BETWEEN ? AND ?
    ''', (date_from, date_to))
    
    active_stations = len(cursor.fetchall())
    
    conn.close()
    
    # Initialize metrics
    total_productive_time = 0  
    total_idle_time = 0
    total_production = 0
    event_count = 0
    
    # Process all events
    for event in events:
        event_type = event['event_type']
        duration = event['duration'] if event['duration'] else DEFAULT_EVENT_DURATION
        count = event['count'] if event['count'] else 0
        
        event_count += 1
        
        if event_type in ['working', 'product_count']:
            total_productive_time += duration
            if event_type == 'product_count':
                total_production += count
        elif event_type == 'idle':
            total_idle_time += duration
    
    # Calculate aggregate metrics
    total_tracked_time = total_productive_time + total_idle_time
    avg_utilization = (total_productive_time / total_tracked_time * 100) if total_tracked_time > 0 else 0
    
    # Average production rate
    productive_hours = total_productive_time / 3600
    avg_production_rate = (total_production / productive_hours) if productive_hours > 0 else 0
    
    # Average units per worker
    units_per_active_worker = (total_production / active_workers) if active_workers > 0 else 0
    
    # Average units per workstation
    units_per_active_station = (total_production / active_stations) if active_stations > 0 else 0
    
    return {
        'date_range': {
            'from': date_from,
            'to': date_to
        },
        'workforce': {
            'total_workers': total_workers,
            'active_workers': active_workers,
            'inactive_workers': total_workers - active_workers
        },
        'workstations': {
            'total_stations': total_stations,
            'active_stations': active_stations,
            'inactive_stations': total_stations - active_stations
        },
        'productivity': {
            'total_productive_time_seconds': total_productive_time,
            'total_productive_time_hours': round(productive_hours, 2),
            'total_idle_time_seconds': total_idle_time,
            'total_idle_time_hours': round(total_idle_time / 3600, 2),
            'average_utilization_percentage': round(avg_utilization, 2)
        },
        'production': {
            'total_units_produced': total_production,
            'average_production_rate_units_per_hour': round(avg_production_rate, 2),
            'units_per_active_worker': round(units_per_active_worker, 2),
            'units_per_active_station': round(units_per_active_station, 2)
        },
        'events': {
            'total_events': event_count,
            'average_events_per_worker': round(event_count / active_workers, 2) if active_workers > 0 else 0
        }
    }

def seed_initial_data(cursor):
    """Seed initial workers and workstations"""
    workers = [
        (1, 'Alice Johnson', 'alice@factory.com'),
        (2, 'Bob Smith', 'bob@factory.com'),
        (3, 'Carol Williams', 'carol@factory.com'),
        (4, 'David Brown', 'david@factory.com'),
        (5, 'Emma Davis', 'emma@factory.com'),
        (6, 'Frank Miller', 'frank@factory.com'),
    ]
    
    workstations = [
        (1, 'Assembly Line A', 'Assembly'),
        (2, 'Assembly Line B', 'Assembly'),
        (3, 'Quality Control', 'QC'),
        (4, 'Packaging Station', 'Packaging'),
        (5, 'Welding Station', 'Welding'),
        (6, 'Inspection Point', 'Inspection'),
    ]
    
    cursor.executemany('INSERT INTO workers (worker_id, name, email) VALUES (?, ?, ?)', workers)
    cursor.executemany('INSERT INTO workstations (station_id, name, type) VALUES (?, ?, ?)', workstations)

def seed_sample_events(cursor, days=7):
    """Seed realistic sample events for the past N days"""
    event_type_distribution = ['working', 'working', 'working', 'working', 'working', 'working',
                               'product_count', 'product_count', 'idle', 'idle', 'idle', 'absent']
    
    # Anchor to midnight so hour offsets land inside the 8 AM - 6 PM shift
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    base_date = today - timedelta(days=days)

    for day_offset in range(days):
        for worker_id in range(1, 7):
            # Create 8-12 events per worker per day
            num_events = random.randint(8, 12)
            
            for _ in range(num_events):
                # Random time between 8 AM and 6 PM
                hour = random.randint(8, 17)
                minute = random.randint(0, 59)
                
                event_date = base_date + timedelta(days=day_offset, hours=hour, minutes=minute)
                event_type = random.choice(event_type_distribution)
                station_id = random.randint(1, 6)
                duration = random.randint(300, 1800)  
                confidence = round(random.uniform(0.75, 0.99), 2)
                count = random.randint(1, 5) if event_type == 'product_count' else None
                
                cursor.execute('''
                    INSERT INTO events (worker_id, station_id, event_type, timestamp, duration, confidence, count)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (worker_id, station_id, event_type, event_date.isoformat(), duration, confidence, count))

@app.route('/api/workers', methods=['GET'])
def get_workers():
    """Get all workers"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM workers')
    workers = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(workers)

@app.route('/api/workstations', methods=['GET'])
def get_workstations():
    """Get all workstations"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM workstations')
    stations = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(stations)

@app.route('/api/events', methods=['POST'])
def create_event():
    """Ingest AI-generated event data from CCTV systems
    
    Expected JSON format:
    {
        "timestamp": "2026-01-15T10:15:00Z",
        "worker_id": "W1",
        "workstation_id": "S3",
        "event_type": "working|idle|absent|product_count",
        "confidence": 0.93,
        "count": 1 (optional, for product_count events)
    }
    """
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['timestamp', 'worker_id', 'workstation_id', 'event_type', 'confidence']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Parse worker_id and workstation_id 
        worker_id = int(str(data['worker_id']).replace('W', '').replace('S', ''))
        station_id = int(str(data['workstation_id']).replace('W', '').replace('S', ''))
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Insert event
        cursor.execute('''
            INSERT INTO events (worker_id, station_id, event_type, timestamp, duration, confidence, count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            worker_id,
            station_id,
            data['event_type'],
            data['timestamp'],
            data.get('duration'),
            data['confidence'],
            data.get('count')
        ))
        
        conn.commit()
        event_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'success': True,
            'event_id': event_id,
            'message': 'Event ingested successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get all events with optional filters"""
    worker_id = request.args.get('worker_id')
    station_id = request.args.get('station_id')
    
    conn = get_db()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM events'
    params = []
    
    if worker_id:
        query += ' WHERE worker_id = ?'
        params.append(worker_id)
    
    if station_id:
        query += ' AND station_id = ?' if params else ' WHERE station_id = ?'
        params.append(station_id)
    
    query += ' ORDER BY timestamp DESC'
    
    cursor.execute(query, params)
    events = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(events)

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get productivity metrics for workers"""
    worker_id = request.args.get('worker_id')
    date = request.args.get('date')
    
    conn = get_db()
    cursor = conn.cursor()
    
    if worker_id:
        if date:
            cursor.execute('''
                SELECT * FROM productivity_metrics 
                WHERE worker_id = ? AND date = ?
            ''', (worker_id, date))
        else:
            cursor.execute('SELECT * FROM productivity_metrics WHERE worker_id = ?', (worker_id,))
    else:
        cursor.execute('SELECT * FROM productivity_metrics')
    
    metrics = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(metrics)

@app.route('/api/metrics/calculate', methods=['POST'])
def calculate_metrics():
    """Calculate productivity metrics for workers based on recent events
    
    This endpoint processes events and computes:
    - Working time (working + product_count events)
    - Idle time (idle events)
    - Productivity score (working time / total tracked time)
    - Product count (sum of count from product_count events)
    """
    try:
        data = request.json
        worker_id = data.get('worker_id')
        date = data.get('date')
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Build query to get events for the worker on the specified date
        query = 'SELECT event_type, duration, count, confidence FROM events WHERE 1=1'
        params = []
        
        if worker_id:
            query += ' AND worker_id = ?'
            params.append(worker_id)
        
        if date:
            query += ' AND DATE(timestamp) = ?'
            params.append(date)
        
        cursor.execute(query, params)
        events = cursor.fetchall()
        
        # Calculate metrics
        working_time = 0
        idle_time = 0
        product_count = 0
        high_confidence_events = 0
        
        for event in events:
            event_type = event['event_type']
            duration = event['duration'] or 300  
            confidence = event['confidence'] or 1.0
            count = event['count'] or 0
            
            if event_type == 'working':
                working_time += duration
                if confidence >= 0.8:
                    high_confidence_events += 1
            elif event_type == 'idle':
                idle_time += duration
            elif event_type == 'product_count':
                product_count += count
                working_time += duration
            elif event_type == 'absent':
                # Absent doesn't count toward productivity
                pass
        
        total_tracked_time = working_time + idle_time
        productivity_score = (working_time / total_tracked_time) if total_tracked_time > 0 else 0
        productivity_score = round(productivity_score, 2)
        
        conn.close()
        
        return jsonify({
            'worker_id': worker_id,
            'date': date,
            'working_time_seconds': working_time,
            'idle_time_seconds': idle_time,
            'total_tracked_time_seconds': total_tracked_time,
            'productivity_score': productivity_score,
            'product_count': product_count,
            'high_confidence_events': high_confidence_events,
            'total_events': len(events)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/metrics/worker/<int:worker_id>', methods=['GET'])
def get_worker_metrics(worker_id):
    """Get comprehensive worker-level metrics
    
    Query params:
    - date_from: Start date (YYYY-MM-DD), defaults to 7 days ago
    - date_to: End date (YYYY-MM-DD), defaults to today
    
    Returns:
    - Active time, idle time, absent time
    - Utilization percentage
    - Total units produced, units per hour, units per shift
    - Event breakdown by type
    """
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        metrics = calculate_worker_metrics(worker_id, date_from, date_to)
        return jsonify(metrics), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/metrics/workers/all', methods=['GET'])
def get_all_workers_metrics():
    """Get worker metrics for all workers
    
    Query params:
    - date_from: Start date (YYYY-MM-DD), defaults to 7 days ago
    - date_to: End date (YYYY-MM-DD), defaults to today
    
    Returns:
    - Array of worker metrics sorted by utilization percentage (descending)
    """
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT worker_id FROM workers ORDER BY worker_id')
        worker_ids = [row['worker_id'] for row in cursor.fetchall()]
        conn.close()
        
        all_metrics = [calculate_worker_metrics(wid, date_from, date_to) for wid in worker_ids]
        # Sort by utilization percentage 
        all_metrics.sort(key=lambda x: x['utilization_percentage'], reverse=True)
        
        return jsonify(all_metrics), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/metrics/workstation/<int:station_id>', methods=['GET'])
def get_workstation_metrics(station_id):
    """Get comprehensive workstation-level metrics
    
    Query params:
    - date_from: Start date (YYYY-MM-DD), defaults to 7 days ago
    - date_to: End date (YYYY-MM-DD), defaults to today
    
    Returns:
    - Occupancy time, productive time, idle time
    - Utilization percentage
    - Total units produced, throughput rate (units/hour), units per day
    - Unique workers, days active
    """
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        metrics = calculate_workstation_metrics(station_id, date_from, date_to)
        return jsonify(metrics), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/metrics/workstations/all', methods=['GET'])
def get_all_workstations_metrics():
    """Get workstation metrics for all workstations
    
    Query params:
    - date_from: Start date (YYYY-MM-DD), defaults to 7 days ago
    - date_to: End date (YYYY-MM-DD), defaults to today
    
    Returns:
    - Array of workstation metrics sorted by utilization percentage (descending)
    """
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT station_id FROM workstations ORDER BY station_id')
        station_ids = [row['station_id'] for row in cursor.fetchall()]
        conn.close()
        
        all_metrics = [calculate_workstation_metrics(sid, date_from, date_to) for sid in station_ids]
        # Sort by utilization percentage 
        all_metrics.sort(key=lambda x: x['utilization_percentage'], reverse=True)
        
        return jsonify(all_metrics), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/metrics/factory', methods=['GET'])
def get_factory_metrics():
    """Get comprehensive factory-level metrics
    
    Query params:
    - date_from: Start date (YYYY-MM-DD), defaults to 7 days ago
    - date_to: End date (YYYY-MM-DD), defaults to today
    
    Returns:
    - Workforce and workstation utilization
    - Total productive/idle time
    - Total production count
    - Average production rate
    - Average utilization percentage
    """
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        metrics = calculate_factory_metrics(date_from, date_to)
        return jsonify(metrics), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """Get dashboard summary data with comprehensive productivity analytics"""
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Get factory-wide metrics
        factory_metrics = calculate_factory_metrics(date_from, date_to)
        
        # Get all worker metrics
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT worker_id FROM workers ORDER BY worker_id')
        worker_ids = [row['worker_id'] for row in cursor.fetchall()]
        conn.close()
        
        worker_metrics = [calculate_worker_metrics(wid, date_from, date_to) for wid in worker_ids]
        worker_metrics.sort(key=lambda x: x['utilization_percentage'], reverse=True)
        
        return jsonify({
            'factory': factory_metrics,
            'workers': worker_metrics,
            'generated_at': datetime.now().isoformat()
        }), 200
    except Exception as e:
        import traceback
        print(f'Dashboard Error: {str(e)}')
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 400

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

@app.route('/api/admin/seed-data', methods=['POST'])
def admin_seed_data():
    """Admin endpoint to refresh all dummy data
    
    Clears all existing data and resets to fresh sample data.
    Useful for evaluators to reset the system without manually editing the database.
    
    Query params:
    - days: number of days of sample data to generate (default: 7)
    """
    try:
        # Check if database exists, if not initialize it
        if not os.path.exists(DATABASE):
            init_db()
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Clear existing events and metrics but keep workers and workstations
        cursor.execute('DELETE FROM events')
        cursor.execute('DELETE FROM productivity_metrics')
        
        # Seed new sample events
        days = request.args.get('days', 7, type=int)
        seed_sample_events(cursor, days=days)
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Database refreshed with {days} days of sample data',
            'events_generated': True
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/seed-custom-event', methods=['POST'])
def admin_seed_custom_event():
    """Admin endpoint to add a single custom event
    
    Useful for manual testing and scenario simulation.
    
    Request body:
    {
        "worker_id": 1,
        "station_id": 3,
        "event_type": "working|idle|absent|product_count",
        "timestamp": "2026-01-24T10:15:00Z",
        "duration": 300,
        "confidence": 0.95,
        "count": 2 (optional, for product_count)
    }
    """
    try:
        data = request.json
        
        required_fields = ['worker_id', 'station_id', 'event_type', 'timestamp']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        if data['event_type'] not in ['working', 'idle', 'absent', 'product_count']:
            return jsonify({'error': 'Invalid event_type'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO events (worker_id, station_id, event_type, timestamp, duration, confidence, count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['worker_id'],
            data['station_id'],
            data['event_type'],
            data['timestamp'],
            data.get('duration', 300),
            data.get('confidence', 1.0),
            data.get('count')
        ))
        
        conn.commit()
        event_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'success': True,
            'event_id': event_id,
            'message': 'Custom event added successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/admin/database-info', methods=['GET'])
def admin_database_info():
    """Admin endpoint to get database statistics
    
    Returns counts and information about current database state.
    """
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM workers')
        worker_count = dict(cursor.fetchone())['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM workstations')
        station_count = dict(cursor.fetchone())['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM events')
        event_count = dict(cursor.fetchone())['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM productivity_metrics')
        metric_count = dict(cursor.fetchone())['count']
        
        cursor.execute('SELECT MIN(timestamp) as min_date FROM events')
        min_date = dict(cursor.fetchone())['min_date']
        
        cursor.execute('SELECT MAX(timestamp) as max_date FROM events')
        max_date = dict(cursor.fetchone())['max_date']
        
        conn.close()
        
        return jsonify({
            'workers': worker_count,
            'workstations': station_count,
            'events': event_count,
            'productivity_metrics': metric_count,
            'date_range': {
                'from': min_date,
                'to': max_date
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    # Seed initial events on first run
    if os.path.exists(DATABASE):
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) as count FROM events')
            event_count = dict(cursor.fetchone())['count']
            conn.close()
            
            # If no events exist, seed sample data
            if event_count == 0:
                print("Seeding sample events...")
                conn = get_db()
                cursor = conn.cursor()
                try:
                    seed_sample_events(cursor, days=7)
                    conn.commit()
                    print("✓ Sample events seeded on initialization")
                except Exception as e:
                    print(f"Error seeding events: {e}")
                    import traceback
                    traceback.print_exc()
                    conn.rollback()
                finally:
                    conn.close()
        except Exception as e:
            print(f"Error checking/seeding events: {e}")
            import traceback
            traceback.print_exc()
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)
