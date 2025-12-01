import React from 'react';
import './ResponseDisplay.css';

function ResponseDisplay({ response }) {
  if (!response) return null;

  return (
    <div className="response-container">
      <div className="answer-section">
        <h2>Answer</h2>
        <div className="answer-content">
          {response.answer}
        </div>
        <div className="confidence-score">
          Confidence: {(response.confidence * 100).toFixed(1)}%
        </div>
      </div>

      {response.sources && response.sources.length > 0 && (
        <div className="sources-section">
          <h3>Sources</h3>
          <ul className="sources-list">
            {response.sources.map((source, index) => (
              <li key={index} className="source-item">
                <span className="source-title">{source.title || `Document ${index + 1}`}</span>
                {source.id && <span className="source-id">ID: {source.id}</span>}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default ResponseDisplay;
