import React from 'react';
import './WorkerCard.css';

function WorkerCard({ worker, isSelected, onSelect }) {
  const utilizationLevel = getUtilizationLevel(worker.utilization_percentage);

  return (
    <div 
      className={`worker-card util-${utilizationLevel} ${isSelected ? 'selected' : ''}`}
      onClick={onSelect}
    >
      <div className="card-header">
        <h3>{worker.worker_name}</h3>
        <span className={`utilization-badge util-${utilizationLevel}`}>
          {worker.utilization_percentage.toFixed(1)}%
        </span>
      </div>

      <div className="card-body">
        <div className="metric">
          <span className="label">Active Time</span>
          <span className="value">{worker.active_time_hours.toFixed(1)}h</span>
        </div>

        <div className="metric">
          <span className="label">Idle Time</span>
          <span className="value">{worker.idle_time_hours.toFixed(1)}h</span>
        </div>

        <div className="metric">
          <span className="label">Total Units</span>
          <span className="value highlight">{worker.total_units_produced}</span>
        </div>

        <div className="metric">
          <span className="label">Units/Hour</span>
          <span className="value">{worker.units_per_hour.toFixed(2)}</span>
        </div>

        <div className="metric">
          <span className="label">Units/Shift</span>
          <span className="value">{worker.units_per_shift.toFixed(1)}</span>
        </div>

        <div className="events-info">
          <span className="event-count">
            {worker.event_breakdown.total_events} events
          </span>
        </div>
      </div>

      {isSelected && (
        <div className="expanded-details">
          <div className="details-grid">
            <div>
              <strong>Working Events</strong>
              <p>{worker.event_breakdown.working_events}</p>
            </div>
            <div>
              <strong>Product Events</strong>
              <p>{worker.event_breakdown.product_events}</p>
            </div>
            <div>
              <strong>Idle Events</strong>
              <p>{worker.event_breakdown.idle_events}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function getUtilizationLevel(utilization) {
  if (utilization >= 80) return 'high';
  if (utilization >= 60) return 'medium';
  return 'low';
}

export default WorkerCard;
