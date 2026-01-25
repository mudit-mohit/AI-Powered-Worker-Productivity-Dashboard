"""
Script to seed sample data into the database
"""
import sqlite3
from datetime import datetime, timedelta
import random

DATABASE = 'factory.db'

def seed_events():
    """Seed sample events in CCTV AI format"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Clear existing events
    cursor.execute('DELETE FROM events')
    
    event_types = ['working', 'idle', 'absent', 'product_count']
    base_date = datetime.now() - timedelta(days=7)
    
    for day_offset in range(7):
        for worker_id in range(1, 7):
            # Create realistic events throughout the day
            for event_num in range(random.randint(8, 15)):
                # Random time between 8 AM and 6 PM
                hour = random.randint(8, 18)
                minute = random.randint(0, 59)
                
                event_date = base_date + timedelta(days=day_offset, hours=hour, minutes=minute)
                
                # Weight event types
                rand = random.random()
                if rand < 0.6:
                    event_type = 'working'
                    count = None
                elif rand < 0.75:
                    event_type = 'product_count'
                    count = random.randint(1, 5)
                elif rand < 0.85:
                    event_type = 'idle'
                    count = None
                else:
                    event_type = 'absent'
                    count = None
                
                # Randomly assign to different stations
                station_id = random.randint(1, 6)
                duration = random.randint(300, 1800)  
                confidence = round(random.uniform(0.75, 0.99), 2)
                
                cursor.execute('''
                    INSERT INTO events (worker_id, station_id, event_type, timestamp, duration, confidence, count)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (worker_id, station_id, event_type, event_date.isoformat(), duration, confidence, count))
    
    conn.commit()
    conn.close()
    print("✓ Sample events seeded successfully")

def seed_metrics():
    """Seed sample productivity metrics"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Clear existing metrics
    cursor.execute('DELETE FROM productivity_metrics')
    
    base_date = datetime.now().date() - timedelta(days=7)
    
    for worker_id in range(1, 7):
        for day_offset in range(7):
            date = base_date + timedelta(days=day_offset)
            active_time = random.randint(3600, 28800)  
            idle_time = random.randint(0, 3600)  
            productivity_score = round(random.uniform(0.6, 1.0), 2)
            
            cursor.execute('''
                INSERT INTO productivity_metrics (worker_id, date, active_time, idle_time, productivity_score)
                VALUES (?, ?, ?, ?, ?)
            ''', (worker_id, date.isoformat(), active_time, idle_time, productivity_score))
    
    conn.commit()
    conn.close()
    print("✓ Sample metrics seeded successfully")

if __name__ == '__main__':
    seed_events()
    seed_metrics()
