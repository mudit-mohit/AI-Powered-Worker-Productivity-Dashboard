import React, { useState, useEffect } from 'react';
import './WorkstationsSection.css';

function WorkstationsSection({ selectedStation, onSelectStation }) {
  const [workstations, setWorkstations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('cards');
  const [sortBy, setSortBy] = useState('utilization');

  useEffect(() => {
    fetchWorkstationMetrics();
  }, []);

  const fetchWorkstationMetrics = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:5000/api/metrics/workstations/all');
      if (!response.ok) throw new Error('Failed to fetch workstation metrics');
      
      const data = await response.json();
      setWorkstations(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Error fetching workstations:', err);
      setWorkstations([]);
    } finally {
      setLoading(false);
    }
  };

  const sortedStations = [...workstations].sort((a, b) => {
    switch (sortBy) {
      case 'utilization':
        return b.utilization_percentage - a.utilization_percentage;
      case 'production':
        return b.total_units_produced - a.total_units_produced;
      case 'throughput':
        return b.throughput_rate_units_per_hour - a.throughput_rate_units_per_hour;
      case 'name':
        return a.station_name.localeCompare(b.station_name);
      default:
        return 0;
    }
  });

  if (loading) {
    return <div className="workstations-section">Loading workstation data...</div>;
  }

  return (
    <div className="workstations-section">
      <div className="section-header">
        <h2>🏗️ Workstations ({workstations.length})</h2>
        <div className="section-controls">
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} className="sort-select">
            <option value="utilization">Sort by Utilization</option>
            <option value="production">Sort by Production</option>
            <option value="throughput">Sort by Throughput</option>
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
        <div className="stations-grid">
          {sortedStations.map(station => (
            <div 
              key={station.station_id} 
              className={`station-card util-${getUtilizationLevel(station.utilization_percentage)} ${selectedStation === station.station_id ? 'selected' : ''}`}
              onClick={() => onSelectStation(station.station_id)}
            >
              <div className="card-header">
                <h3>{station.station_name}</h3>
                <span className={`utilization-badge util-${getUtilizationLevel(station.utilization_percentage)}`}>
                  {station.utilization_percentage.toFixed(1)}%
                </span>
              </div>

              <div className="card-body">
                <div className="metric">
                  <span className="label">Type</span>
                  <span className="value">{station.station_type}</span>
                </div>

                <div className="metric">
                  <span className="label">Occupancy</span>
                  <span className="value">{station.occupancy_time_hours.toFixed(1)}h</span>
                </div>

                <div className="metric">
                  <span className="label">Total Units</span>
                  <span className="value highlight">{station.total_units_produced}</span>
                </div>

                <div className="metric">
                  <span className="label">Throughput</span>
                  <span className="value">{station.throughput_rate_units_per_hour.toFixed(2)} u/h</span>
                </div>

                <div className="metric">
                  <span className="label">Units/Day</span>
                  <span className="value">{station.units_per_day.toFixed(1)}</span>
                </div>

                <div className="station-info">
                  <span>{station.unique_workers} workers • {station.days_active} days</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <table className="stations-table">
          <thead>
            <tr>
              <th>Station Name</th>
              <th>Type</th>
              <th>Utilization</th>
              <th>Total Units</th>
              <th>Throughput</th>
              <th>Units/Day</th>
              <th>Workers</th>
            </tr>
          </thead>
          <tbody>
            {sortedStations.map(station => (
              <tr 
                key={station.station_id} 
                className={`station-row ${selectedStation === station.station_id ? 'selected' : ''}`}
                onClick={() => onSelectStation(station.station_id)}
              >
                <td className="station-name">{station.station_name}</td>
                <td>{station.station_type}</td>
                <td>
                  <span className={`utilization-badge util-${getUtilizationLevel(station.utilization_percentage)}`}>
                    {station.utilization_percentage.toFixed(1)}%
                  </span>
                </td>
                <td className="production-cell">{station.total_units_produced}</td>
                <td>{station.throughput_rate_units_per_hour.toFixed(2)}</td>
                <td>{station.units_per_day.toFixed(1)}</td>
                <td>{station.unique_workers}</td>
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

export default WorkstationsSection;
