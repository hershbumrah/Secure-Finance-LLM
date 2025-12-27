import React, { useState } from 'react';
import './QueryInput.css';

function QueryInput({ onSubmit, loading, availableDocuments = [] }) {
  const [query, setQuery] = useState('');
  const [selectedDocument, setSelectedDocument] = useState('all');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim() && !loading) {
      const filters = selectedDocument !== 'all' ? { source_file: selectedDocument } : {};
      onSubmit(query, filters);
    }
  };

  return (
    <div className="query-input-container">
      <form onSubmit={handleSubmit}>
        {availableDocuments.length > 0 && (
          <div className="filter-group">
            <label htmlFor="document-filter">Filter by document:</label>
            <select
              id="document-filter"
              className="document-select"
              value={selectedDocument}
              onChange={(e) => setSelectedDocument(e.target.value)}
              disabled={loading}
            >
              <option value="all">All Documents</option>
              {availableDocuments.map((doc) => (
                <option key={doc} value={doc}>{doc}</option>
              ))}
            </select>
          </div>
        )}
        
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
