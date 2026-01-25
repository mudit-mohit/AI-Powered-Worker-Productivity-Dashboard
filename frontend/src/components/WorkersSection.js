import React, { useState } from 'react';
import WorkerCard from './WorkerCard';
import './WorkersSection.css';

function WorkersSection({ workers, selectedWorker, onSelectWorker }) {
  const [viewMode, setViewMode] = useState('cards'); 
  const [sortBy, setSortBy] = useState('utilization'); 

  const sortedWorkers = [...(workers || [])].sort((a, b) => {
    switch (sortBy) {
      case 'utilization':
        return b.utilization_percentage - a.utilization_percentage;
      case 'production':
        return b.total_units_produced - a.total_units_produced;
      case 'name':
        return a.worker_name.localeCompare(b.worker_name);
      default:
        return 0;
    }
  });

  return (
    <div className="workers-section">
      <div className="section-header">
        <h2>👷 Workers ({workers?.length || 0})</h2>
        <div className="section-controls">
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} className="sort-select">
            <option value="utilization">Sort by Utilization</option>
            <option value="production">Sort by Production</option>
            <option value="name">Sort by Name</option>
          </select>
          
          <div className="view-toggle">
            <button 
              className={`toggle-btn ${viewMode === 'cards' ? 'active' : ''}`}
              onClick={() => setViewMode('cards')}
              title="Card View"
            >
              ☰
            </button>
            <button 
              className={`toggle-btn ${viewMode === 'table' ? 'active' : ''}`}
              onClick={() => setViewMode('table')}
              title="Table View"
            >
              ≡
            </button>
          </div>
        </div>
      </div>

      {viewMode === 'cards' ? (
        <div className="workers-grid">
          {sortedWorkers.map(worker => (
            <WorkerCard
              key={worker.worker_id}
              worker={worker}
              isSelected={selectedWorker === worker.worker_id}
              onSelect={() => onSelectWorker(worker.worker_id)}
            />
          ))}
        </div>
      ) : (
        <table className="workers-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Utilization</th>
              <th>Active Time</th>
              <th>Total Units</th>
              <th>Units/Hour</th>
              <th>Units/Shift</th>
            </tr>
          </thead>
          <tbody>
            {sortedWorkers.map(worker => (
              <tr 
                key={worker.worker_id} 
                className={`worker-row ${selectedWorker === worker.worker_id ? 'selected' : ''}`}
                onClick={() => onSelectWorker(worker.worker_id)}
              >
                <td className="worker-name">{worker.worker_name}</td>
                <td>
                  <span className={`utilization-badge util-${getUtilizationLevel(worker.utilization_percentage)}`}>
                    {worker.utilization_percentage.toFixed(1)}%
                  </span>
                </td>
                <td>{worker.active_time_hours.toFixed(1)}h</td>
                <td className="production-cell">{worker.total_units_produced}</td>
                <td>{worker.units_per_hour.toFixed(2)}</td>
                <td>{worker.units_per_shift.toFixed(1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

function getUtilizationLevel(utilization) {
  if (utilization >= 80) return 'high';
  if (utilization >= 60) return 'medium';
  return 'low';
}

export default WorkersSection;
