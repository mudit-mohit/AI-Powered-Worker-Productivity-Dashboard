import React from 'react';
import './FactorySummary.css';

function FactorySummary({ factory }) {
  if (!factory) return null;

  const {
    workforce,
    workstations,
    productivity,
    production,
    events
  } = factory;

  return (
    <div className="factory-summary">
      <h2>📊 Factory Overview</h2>
      
      <div className="summary-grid">
        {/* Workforce Summary */}
        <div className="summary-card workforce">
          <div className="card-header">Workforce</div>
          <div className="metric-row">
            <span className="metric-label">Active Workers</span>
            <span className="metric-value">{workforce?.active_workers || 0}</span>
          </div>
          <div className="metric-row">
            <span className="metric-label">Total Workers</span>
            <span className="metric-value">{workforce?.total_workers || 0}</span>
          </div>
          <div className="metric-row">
            <span className="metric-label">Inactive</span>
            <span className="metric-value danger">{workforce?.inactive_workers || 0}</span>
          </div>
        </div>

        {/* Workstations Summary */}
        <div className="summary-card workstations">
          <div className="card-header">Workstations</div>
          <div className="metric-row">
            <span className="metric-label">Active Stations</span>
            <span className="metric-value">{workstations?.active_stations || 0}</span>
          </div>
          <div className="metric-row">
            <span className="metric-label">Total Stations</span>
            <span className="metric-value">{workstations?.total_stations || 0}</span>
          </div>
          <div className="metric-row">
            <span className="metric-label">Inactive</span>
            <span className="metric-value danger">{workstations?.inactive_stations || 0}</span>
          </div>
        </div>

        {/* Productivity Summary */}
        <div className="summary-card productivity">
          <div className="card-header">Productivity</div>
          <div className="metric-row">
            <span className="metric-label">Avg Utilization</span>
            <span className="metric-value success">
              {(productivity?.average_utilization_percentage || 0).toFixed(1)}%
            </span>
          </div>
          <div className="metric-row">
            <span className="metric-label">Total Active Time</span>
            <span className="metric-value">{(productivity?.total_productive_time_hours || 0).toFixed(1)}h</span>
          </div>
          <div className="metric-row">
            <span className="metric-label">Total Idle Time</span>
            <span className="metric-value">{(productivity?.total_idle_time_hours || 0).toFixed(1)}h</span>
          </div>
        </div>

        {/* Production Summary */}
        <div className="summary-card production">
          <div className="card-header">Production</div>
          <div className="metric-row">
            <span className="metric-label">Total Units</span>
            <span className="metric-value highlight">{production?.total_units_produced || 0}</span>
          </div>
          <div className="metric-row">
            <span className="metric-label">Production Rate</span>
            <span className="metric-value">{(production?.average_production_rate_units_per_hour || 0).toFixed(2)} u/h</span>
          </div>
          <div className="metric-row">
            <span className="metric-label">Units per Worker</span>
            <span className="metric-value">{(production?.units_per_active_worker || 0).toFixed(1)}</span>
          </div>
        </div>

        {/* Events Summary */}
        <div className="summary-card events">
          <div className="card-header">Events</div>
          <div className="metric-row">
            <span className="metric-label">Total Events</span>
            <span className="metric-value">{events?.total_events || 0}</span>
          </div>
          <div className="metric-row">
            <span className="metric-label">Avg Events/Worker</span>
            <span className="metric-value">{(events?.average_events_per_worker || 0).toFixed(1)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default FactorySummary;
