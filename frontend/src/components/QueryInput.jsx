import React, { useState } from 'react';
import './QueryInput.css';

function QueryInput({ onSubmit, loading }) {
  const [query, setQuery] = useState('');
  const [filters] = useState({});

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim() && !loading) {
      onSubmit(query, filters);
    }
  };

  return (
    <div className="query-input-container">
      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <textarea
            className="query-textarea"
            placeholder="Ask a question about your financial documents..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            rows={4}
            disabled={loading}
          />
        </div>
        
        <div className="button-group">
          <button
            type="submit"
            className="submit-btn"
            disabled={loading || !query.trim()}
          >
            {loading ? 'Processing...' : 'Submit Query'}
          </button>
          <button
            type="button"
            className="clear-btn"
            onClick={() => setQuery('')}
            disabled={loading}
          >
            Clear
          </button>
        </div>
      </form>
    </div>
  );
}

export default QueryInput;
