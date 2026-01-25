import React from 'react';
import './DateRangeFilter.css';

function DateRangeFilter({ dateRange, onDateChange }) {
  const handleFromChange = (e) => {
    onDateChange({
      ...dateRange,
      from: e.target.value
    });
  };

  const handleToChange = (e) => {
    onDateChange({
      ...dateRange,
      to: e.target.value
    });
  };

  const handleQuickRange = (days) => {
    const toDate = new Date();
    const fromDate = new Date();
    fromDate.setDate(fromDate.getDate() - days);

    onDateChange({
      from: fromDate.toISOString().split('T')[0],
      to: toDate.toISOString().split('T')[0]
    });
  };

  return (
    <div className="date-range-filter">
      <div className="filter-section">
        <div className="date-inputs">
          <div className="date-group">
            <label htmlFor="date-from">From:</label>
            <input 
              id="date-from"
              type="date" 
              value={dateRange.from}
              onChange={handleFromChange}
              className="date-input"
            />
          </div>
          <div className="date-group">
            <label htmlFor="date-to">To:</label>
            <input 
              id="date-to"
              type="date" 
              value={dateRange.to}
              onChange={handleToChange}
              className="date-input"
            />
          </div>
        </div>

        <div className="quick-range-buttons">
          <button onClick={() => handleQuickRange(7)} className="quick-btn">Last 7 days</button>
          <button onClick={() => handleQuickRange(14)} className="quick-btn">Last 14 days</button>
          <button onClick={() => handleQuickRange(30)} className="quick-btn">Last 30 days</button>
        </div>
      </div>
    </div>
  );
}

export default DateRangeFilter;
