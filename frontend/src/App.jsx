import React, { useState } from 'react';
import './App.css';
import QueryInput from './components/QueryInput';
import ResponseDisplay from './components/ResponseDisplay';
import Login from './components/Login';
import { queryAPI } from './api';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState('');
  const [userId, setUserId] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleLogin = (authToken, user) => {
    setToken(authToken);
    setUserId(user);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    setToken('');
    setUserId('');
    setIsAuthenticated(false);
    setResponse(null);
  };

  const handleQuery = async (query, filters) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await queryAPI(query, userId, token, filters);
      setResponse(result);
    } catch (err) {
      setError(err.message || 'An error occurred while processing your query');
      setResponse(null);
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="App">
        <Login onLogin={handleLogin} />
      </div>
    );
  }

  return (
    <div className="App">
      <header className="app-header">
        <h1>Secure Finance LLM</h1>
        <div className="user-info">
          <span>Logged in as: {userId}</span>
          <button onClick={handleLogout} className="logout-btn">
            Logout
          </button>
        </div>
      </header>

      <main className="app-main">
        <div className="query-section">
          <QueryInput onSubmit={handleQuery} loading={loading} />
        </div>

        <div className="response-section">
          {loading && <div className="loading">Processing your query...</div>}
          {error && <div className="error-message">{error}</div>}
          {response && <ResponseDisplay response={response} />}
        </div>
      </main>
    </div>
  );
}

export default App;
