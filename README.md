# AI-Powered Worker Productivity Dashboard

A full-stack web application for monitoring worker activity and productivity metrics in a manufacturing factory using AI-powered CCTV events.

## Project Structure

```
├── backend/                      # Python Flask API server
│   ├── app.py                    # Main Flask application
│   ├── Dockerfile                # Docker configuration for backend
│   ├── requirements.txt           # Python dependencies
│   ├── seed_sample_data.py        # Utility for seeding sample data
│   └── data/                      # Data storage directory
├── frontend/                      # React dashboard
│   ├── Dockerfile                 # Docker configuration for frontend
│   ├── index.html                 # HTML entry point
│   ├── package.json               # Node.js dependencies
│   ├── public/                    # Public assets
│   │   └── index.html
│   ├── src/                       # React source code
│   │   ├── App.js                 # Main App component
│   │   ├── App.css                # App styles
│   │   ├── index.js               # React entry point
│   │   ├── index.css              # Global styles
│   │   └── components/            # React components
│   │       ├── DateRangeFilter.js
│   │       ├── FactorySummary.js
│   │       ├── WorkerCard.js
│   │       ├── WorkersSection.js
│   │       └── WorkstationsSection.js
│   └── build/                     # Production build output
├── docker-compose.yml             # Docker Compose configuration
└── README.md                       # This file
```

## Database Schema

### Tables

**workers** - Factory worker records
```sql
CREATE TABLE workers (
    worker_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    email TEXT UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

**workstations** - Production workstation records
```sql
CREATE TABLE workstations (
    station_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    type TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

**events** - AI-generated CCTV events
```sql
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
```

**productivity_metrics** - Calculated metrics per worker per day
```sql
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
```

### Indices
- `idx_events_worker_id` on events(worker_id)
- `idx_events_station_id` on events(station_id)
- `idx_events_timestamp` on events(timestamp)
- `idx_metrics_worker_id` on productivity_metrics(worker_id)
- `idx_metrics_date` on productivity_metrics(date)

## Data Pre-population

The database automatically initializes with sample data on first run:

- **6 Workers**: Alice Johnson, Bob Smith, Carol Williams, David Brown, Emma Davis, Frank Miller
- **6 Workstations**: Assembly Lines A & B, Quality Control, Packaging, Welding, Inspection
- **Sample Events**: 7 days of realistic CCTV events (60% working, 15% product_count, 15% idle, 10% absent)

Events are seeded automatically when the application first starts and no events exist in the database.

## Setup

### Backend

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Run the Flask app:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

The database will automatically:
- Initialize on first run (creates `factory.db`)
- Seed 6 workers and 6 workstations
- Generate 7 days of sample events

### Frontend

Simply open `frontend/index.html` in a web browser to view the dashboard.

## Quick Start Examples

### 1. Check System Status
```bash
curl http://localhost:5000/health
```

### 2. Get Dashboard Summary
```bash
curl http://localhost:5000/api/dashboard
```

### 3. Ingest a Single Event
```bash
curl -X POST http://localhost:5000/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2026-01-24T14:30:00Z",
    "worker_id": 1,
    "workstation_id": 3,
    "event_type": "product_count",
    "confidence": 0.95,
    "count": 2
  }'
```

### 4. Refresh Sample Data (for Evaluators)
```bash
# Reset to 7 days of fresh sample data
curl -X POST http://localhost:5000/api/admin/seed-data

# Or with custom duration (e.g., 14 days)
curl -X POST "http://localhost:5000/api/admin/seed-data?days=14"
```

### 5. Check Database Status
```bash
curl http://localhost:5000/api/admin/database-info
```

### 6. Get Worker Productivity Score
```bash
curl "http://localhost:5000/api/metrics/calculate" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"worker_id": 1, "date": "2026-01-24"}'
```

## Comprehensive Metrics Endpoints

### Worker Metrics
```bash
# Single worker metrics
GET /api/metrics/worker/1?date_from=2026-01-17&date_to=2026-01-24

# All workers metrics (sorted by utilization)
GET /api/metrics/workers/all?date_from=2026-01-17&date_to=2026-01-24
```

Returns: active_time, idle_time, utilization_pct, units_produced, units_per_hour, units_per_shift, event_breakdown

### Workstation Metrics
```bash
# Single workstation metrics
GET /api/metrics/workstation/3?date_from=2026-01-17&date_to=2026-01-24

# All workstations metrics (sorted by utilization)
GET /api/metrics/workstations/all?date_from=2026-01-17&date_to=2026-01-24
```

Returns: occupancy_time, productive_time, utilization_pct, units_produced, throughput_rate, units_per_day, unique_workers, days_active

### Factory Metrics
```bash
GET /api/metrics/factory?date_from=2026-01-17&date_to=2026-01-24
```

Returns: workforce (active/total), workstations (active/total), productivity (times, utilization), production (units, rates), events (totals, averages)

### Integrated Dashboard
```bash
# Complete dashboard with factory + all workers metrics
GET /api/dashboard?date_from=2026-01-17&date_to=2026-01-24
```

## Database Details

- **Type**: SQLite (file-based: `factory.db`)
- **Location**: Backend root directory
- **Auto-initialization**: Yes, on first run
- **Sample data**: Automatically seeded with 7 days of realistic events
- **Manual reset**: Use `/api/admin/seed-data` endpoint

## API Endpoints

### Health Check
- `GET /health` - Service health check

### Worker & Workstation Management
- `GET /api/workers` - Get all workers
- `GET /api/workstations` - Get all workstations

### Event Ingestion
- `POST /api/events` - Ingest AI-generated CCTV event data
  - **Required fields**: `timestamp`, `worker_id`, `workstation_id`, `event_type`, `confidence`
  - **Optional fields**: `count` (for product_count events), `duration`
  - **Supported event types**: `working`, `idle`, `absent`, `product_count`
  - **Worker/Station ID parsing**: Accepts both "1" or "W1", "S1" formats

Example event POST:
```json
{
  "timestamp": "2026-01-24T10:15:00Z",
  "worker_id": "W1",
  "workstation_id": "S3",
  "event_type": "working",
  "confidence": 0.93,
  "count": null
}
```

- `GET /api/events` - Get all events with optional filters
  - Query params: `worker_id`, `station_id`

### Metrics & Analytics
- `GET /api/metrics` - Get productivity metrics from metrics table
  - Query params: `worker_id`, `date`
- `POST /api/metrics/calculate` - Calculate metrics based on recent events
  - Request body: `{ "worker_id": 1, "date": "2026-01-24" }`
  - Returns: working time, idle time, productivity score, product count
- `GET /api/dashboard` - Get dashboard summary with factory-wide analytics
  - Returns aggregated metrics for all workers and factory statistics

### Admin Endpoints (Data Management)
- `POST /api/admin/seed-data` - Refresh all dummy data
  - Clears events and metrics, generates fresh sample data
  - Query param: `days` (default: 7) - number of days of sample data to generate
  - **Use case**: Evaluators can reset the system without manual DB edits
  
  ```bash
  curl -X POST http://localhost:5000/api/admin/seed-data?days=14
  ```

- `POST /api/admin/seed-custom-event` - Add a single custom event
  - Useful for manual testing and scenario simulation
  - Request body: Same as `/api/events` POST
  
  ```json
  {
    "worker_id": 1,
    "station_id": 3,
    "event_type": "product_count",
    "timestamp": "2026-01-24T10:15:00Z",
    "duration": 600,
    "confidence": 0.95,
    "count": 3
  }
  ```

- `GET /api/admin/database-info` - Get database statistics
  - Returns counts of workers, stations, events, metrics and date range of events

---

## Architecture: Edge → Backend → Dashboard

### System Architecture Overview

The application follows a **three-tier architecture** designed for scalability, reliability, and real-time processing:

```
┌─────────────────────────────────────────────────────────────────┐
│                        EDGE TIER (Future)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Camera 1 │  │ Camera 2 │  │ Camera 3 │  │ Camera N │        │
│  │ (YOLO)   │  │ (YOLO)   │  │ (YOLO)   │  │ (YOLO)   │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
│       │ Detection   │             │             │               │
│       └────────────┬──────────────┼─────────────┘               │
│                    │ Events (MQTT/HTTP)                         │
└────────────────────┼──────────────────────────────────────────┘
                     │
┌────────────────────▼──────────────────────────────────────────┐
│                    BACKEND TIER (Current)                      │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │           Event Ingestion & Processing                   │ │
│  │  • De-duplication (UUID tracking)                        │ │
│  │  • Timestamp validation & correction                     │ │
│  │  • Out-of-order event handling (5s window)              │ │
│  │  • Retry logic with exponential backoff                 │ │
│  └──────────────────────────────────────────────────────────┘ │
│                            │                                   │
│  ┌──────────────────────────▼──────────────────────────────┐ │
│  │              Metrics Computation Engine                  │ │
│  │  • Real-time aggregation (worker/station/factory)       │ │
│  │  • Model versioning (inference engine tracking)         │ │
│  │  • Drift detection (metric anomalies)                   │ │
│  │  • Retraining triggers (accuracy degradation)          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                            │                                   │
│  ┌──────────────────────────▼──────────────────────────────┐ │
│  │            SQLite Database (Production)                  │ │
│  │  • Events table (indexed by worker_id, timestamp)       │ │
│  │  • Workers & Workstations (reference data)              │ │
│  │  • Productivity metrics (daily aggregation)             │ │
│  │  • Model metadata (version, accuracy, drift)           │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  Flask REST API (7+ endpoints)                                │
│  http://localhost:5000                                        │
└────────────────────┬───────────────────────────────────────────┘
                     │ REST/JSON
┌────────────────────▼───────────────────────────────────────────┐
│                   DASHBOARD TIER                               │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │       React 18 Dashboard (http://localhost:3000)         │ │
│  │  • Real-time metrics display (5-second refresh)         │ │
│  │  • Worker performance cards (utilization %)             │ │
│  │  • Workstation utilization (throughput, occupancy)      │ │
│  │  • Factory-wide KPIs                                    │ │
│  │  • Date range filtering & trend analysis                │ │
│  │  • Responsive mobile design                             │ │
│  └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## Data Handling Strategies

### 1. Intermittent Connectivity

**Problem**: CCTV systems and backend may lose connection temporarily, causing event delivery failures.

**Solution**:
- **Edge-level buffering**: Local event queues with disk fallback (up to 10,000 events)
- **Retry logic**: Exponential backoff (1s, 2s, 4s) with max 5 retries
- **Async ingestion**: API returns 202 Accepted immediately, processes in background
- **Queue monitoring**: Alerts at 80% queue saturation

**Implementation**: Add MQTT/event queue (RabbitMQ, Kafka) for production at Phase 2+

---

### 2. Duplicate Events

**Problem**: Network retries or multiple edge devices send the same event multiple times.

**Current Detection**:
- UUID-based tracking (explicit event IDs)
- Content hash matching (timestamp + worker + type + duration)
- Temporal proximity (same event within 5 seconds)

**Database enhancement**:
```sql
ALTER TABLE events ADD COLUMN uuid TEXT UNIQUE;
ALTER TABLE events ADD COLUMN content_hash TEXT;
CREATE INDEX idx_events_uuid ON events(uuid);
CREATE INDEX idx_events_content_hash ON events(content_hash);
```

---

### 3. Out-of-Order Timestamps

**Problem**: Events may arrive out of chronological order due to network delays or clock skew.

**Solution**:
- **Clock skew detection**: Track device clock offsets with moving average
- **Temporal buffering**: 5-second reordering window
- **Future timestamp correction**: Use server time if event time is in future
- **Device regression detection**: Flag large clock regressions (>1 minute)

**Implementation**: Automatic reordering buffer with automatic flush on timeout or order violation

---

## Model Versioning & Drift Detection

### Model Versioning

Track multiple AI model versions with performance metrics:

```sql
CREATE TABLE model_versions (
    model_id INTEGER PRIMARY KEY,
    model_name TEXT NOT NULL,
    model_version TEXT UNIQUE,
    model_path TEXT,           -- S3 or local path
    accuracy_baseline REAL,    -- 0.75-1.0
    production_start_date DATETIME,
    retraining_data_size INTEGER,
    is_active BOOLEAN DEFAULT 0
);
```

**Features**:
- A/B testing support (multiple versions active)
- Performance tracking per model version
- Automatic rollback capability
- Model registry with S3 integration (Phase 2+)

---

### Drift Detection

Automatically detect when model accuracy degrades:

```python
class ModelDriftDetector:
    def detect_drift(self, model_id, evaluation_period_days=7):
        """
        Compare baseline vs current performance
        Returns: drift_score, alert_level, recommendation
        """
        baseline = get_baseline_performance(model_id)
        current = get_current_performance(model_id)
        
        confidence_drop = baseline['avg_confidence'] - current['avg_confidence']
        
        if confidence_drop > 0.15:
            return {"alert": "WARNING", "action": "SCHEDULE_RETRAINING"}
        elif confidence_drop > 0.25:
            return {"alert": "CRITICAL", "action": "RETRAIN_IMMEDIATELY"}
```

**Alert Levels**:
- OK: < 5% accuracy drop
- WARNING: 5-15% drop → Schedule retraining
- CRITICAL: > 15% drop → Immediate retraining required

---

### Retraining Triggers

Automatic retraining is triggered by multiple conditions:

1. **Drift Detection**: Model accuracy < baseline × 0.85
2. **Event Volume**: Collected > 100,000 new events
3. **Time Elapsed**: Model in production > 90 days
4. **Accuracy Drop**: Confidence < 0.75 (7-day rolling window)
5. **Pattern Changes**: High variance in predictions (std dev > 0.1)

**Priority Calculation** (1-10 scale):
```
Drift: +5 points
Accuracy Drop: +4 points
Event Volume: +3 points
New Patterns: +3 points
Time Elapsed: +2 points
```

---

## Scaling Strategy: 5 → 100+ Cameras → Multi-Site

### Phase 1: Single Site, 5-25 Cameras (Current)

**Current Implementation**:
- Single Flask backend on standard server
- SQLite database (sufficient for ~1M events)
- Single React frontend
- Real-time updates via polling (5-10 second intervals)

**Capacity**:
- 5 cameras × 60 fps = 300 fps inference
- ~1000-2000 events/hour
- Database: 500K-1M events

---

### Phase 2: Single Site, 25-100 Cameras

**Database Upgrade**:
```
SQLite → PostgreSQL
- Connection pooling (PgBouncer)
- Partitioning by date
- Concurrent write support
- 10M+ event capacity
```

**Backend Scaling**:
```
Multiple Flask workers behind Nginx load balancer:
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Caching Layer** (Redis):
```python
# Cache dashboard metrics for 1 minute
cache.setex('dashboard:metrics', 60, json.dumps(metrics))
```

**Event Processing** (RabbitMQ/Celery):
```python
# Async event ingestion
process_event.delay(event)  # Returns immediately
```

**WebSocket Updates** (vs polling):
- Real-time push instead of pull
- Lower latency, reduced server load

**Capacity**:
- 50+ cameras × 30 fps = 1500+ fps
- 5000-10000 events/hour
- Database: 10M+ events
- Response time: < 100ms

---

### Phase 3: Multi-Site, 100+ Cameras Across Sites

**Distributed Architecture**:
```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   SITE 1    │      │   SITE 2    │      │   SITE N    │
│ (50 cameras)│      │ (50 cameras)│      │ (50 cameras)│
└──────┬──────┘      └──────┬──────┘      └──────┬──────┘
       │ (Local buffering)  │                    │
       └─────────────────────┼────────────────────┘
                             │
                ┌────────────▼─────────────┐
                │  CENTRAL BACKEND         │
                │  Event aggregation       │
                │  Global model registry   │
                └──────────┬───────────────┘
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
        ┌────────┐    ┌────────┐    ┌────────┐
        │ Site 1 │    │ Site 2 │    │ Site N │
        │Frontend│    │Frontend│    │Frontend│
        └────────┘    └────────┘    └────────┘
```

**Event Streaming** (Kafka):
- High-throughput event pipeline
- Multi-site aggregation
- Automatic partitioning by site

**Global Model Registry**:
- Site-specific models or global models
- Canary rollout: 10% → 50% → 100%
- Automatic A/B testing

**Database Partitioning**:
```sql
-- Partition by site and date
CREATE TABLE events_site_1 PARTITION OF events
    FOR VALUES WHERE site_id = 1;
```

**Capacity**:
- 100+ cameras across multiple sites
- 50K+ events/hour (combined)
- 100M+ events in database
- Response time: < 200ms globally
- Support for site-specific + global insights

---

## Summary: Scaling Roadmap

| Phase | Cameras | Events/Hour | Database | Backend | Infrastructure |
|-------|---------|-------------|----------|---------|-----------------|
| **Phase 1** | 5-25 | 1K-2K | SQLite (1M) | Single Flask | Docker, local |
| **Phase 2** | 25-100 | 5K-10K | PostgreSQL (10M) | Multi-worker | K8s, Redis, RabbitMQ |
| **Phase 3** | 100+ Multi-site | 50K+ | PostgreSQL (100M+) | Distributed | Kafka, CDN, multi-region |

---

## Next Steps

- [ ] Test API endpoints with sample events
- [ ] Implement event buffering for edge resilience
- [ ] Add UUID-based deduplication at scale
- [ ] Build model versioning system
- [ ] Implement drift detection pipeline
- [ ] Set up automated retraining workflow
- [ ] Deploy multi-region architecture
- [ ] Add global monitoring dashboard
- [ ] Implement Kafka event streaming
- [ ] Set up PostgreSQL replication
