import React, { useState } from 'react';
import './App.css';
import QueryInput from './components/QueryInput';
import ResponseDisplay from './components/ResponseDisplay';
import Login from './components/Login';
import FileUpload from './components/FileUpload';
import AdminPanel from './components/AdminPanel';
import { queryAPI } from './api';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState('');
  const [userId, setUserId] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('query'); // 'query' or 'admin'
  const [availableDocuments, setAvailableDocuments] = useState([]);

  const handleLogin = async (authToken, user) => {
    setToken(authToken);
    setUserId(user);
    setIsAuthenticated(true);
    
    // Fetch available documents for filtering
    try {
      const response = await fetch('http://localhost:8000/admin/documents', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setAvailableDocuments(data.documents.map(doc => doc.filename));
      }
    } catch (err) {
      console.error('Failed to fetch documents:', err);
    }
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
      const result = await queryAPI(query, token, filters);
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

      <nav className="app-nav">
        <button 
          className={`nav-btn ${activeTab === 'query' ? 'active' : ''}`}
          onClick={() => setActiveTab('query')}
        >
          Query Documents
        </button>
        <button 
          className={`nav-btn ${activeTab === 'admin' ? 'active' : ''}`}
          onClick={() => setActiveTab('admin')}
        >
          Manage Access (Admin)
        </button>
      </nav>

      <main className="app-main">
        {activeTab === 'query' ? (
          <>
            <div className="upload-section">
              <FileUpload token={token} />
            </div>

            <div className="query-section">
              <QueryInput onSubmit={handleQuery} loading={loading} availableDocuments={availableDocuments} />
            </div>

            <div className="response-section">
              {loading && <div className="loading">Processing your query...</div>}
              {error && <div className="error-message">{error}</div>}
              {response && <ResponseDisplay response={response} />}
            </div>
          </>
        ) : (
          <AdminPanel token={token} />
        )}
      </main>
    </div>
  );
}

export default App;
