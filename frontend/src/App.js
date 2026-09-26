import React, { useState, useEffect } from 'react';
import './App.css';
import FactorySummary from './components/FactorySummary';
import WorkersSection from './components/WorkersSection';
import WorkstationsSection from './components/WorkstationsSection';
import DateRangeFilter from './components/DateRangeFilter';

// Empty default = same-origin requests (Flask serves the build; CRA dev server proxies /api)
const API_BASE_URL = process.env.REACT_APP_API_URL || '';

function App() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dateRange, setDateRange] = useState({
    from: getDefaultFromDate(),
    to: getDefaultToDate()
  });
  const [selectedWorker, setSelectedWorker] = useState(null);
  const [selectedStation, setSelectedStation] = useState(null);

  function getDefaultFromDate() {
    const date = new Date();
    date.setDate(date.getDate() - 7);
    return date.toISOString().split('T')[0];
  }

  function getDefaultToDate() {
    return new Date().toISOString().split('T')[0];
  }

  useEffect(() => {
    fetchDashboard();
  }, [dateRange]);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        date_from: dateRange.from,
        date_to: dateRange.to
      });
      
      const response = await fetch(`${API_BASE_URL}/api/dashboard?${params}`);
      if (!response.ok) throw new Error('Failed to fetch dashboard data');
      
      const data = await response.json();
      setDashboardData(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching dashboard:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDateChange = (newDateRange) => {
    setDateRange(newDateRange);
  };

  const handleWorkerSelect = (workerId) => {
    setSelectedWorker(selectedWorker === workerId ? null : workerId);
  };

  const handleStationSelect = (stationId) => {
    setSelectedStation(selectedStation === stationId ? null : stationId);
  };

  if (error) {
    return (
      <div className="error-container">
        <div className="error-box">
          <h2>⚠️ Connection Error</h2>
          <p>{error}</p>
          <p>Make sure the backend server is running</p>
          <button onClick={fetchDashboard} className="retry-btn">Retry</button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🏭 Worker Productivity Dashboard</h1>
        <p>Real-time monitoring of factory worker activity and productivity metrics</p>
      </header>

      <div className="app-container">
        <DateRangeFilter dateRange={dateRange} onDateChange={handleDateChange} />

        {dashboardData && (
          <>
            <FactorySummary factory={dashboardData.factory} />
            
            <div className="sections-grid">
              <WorkersSection 
                workers={dashboardData.workers} 
                selectedWorker={selectedWorker}
                onSelectWorker={handleWorkerSelect}
              />
              
              <WorkstationsSection 
                dateRange={dateRange}
                selectedStation={selectedStation}
                onSelectStation={handleStationSelect}
              />
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default App;
