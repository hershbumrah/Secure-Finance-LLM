import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './AdminPanel.css';

const AdminPanel = ({ token }) => {
  const [documents, setDocuments] = useState([]);
  const [users, setUsers] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  // Fetch documents and users on mount
  useEffect(() => {
    fetchDocuments();
    fetchUsers();
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await axios.get('http://localhost:8000/admin/documents', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDocuments(response.data.documents || []);
    } catch (error) {
      console.error('Error fetching documents:', error);
      setMessage('Error loading documents');
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await axios.get('http://localhost:8000/admin/users', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUsers(response.data.users || []);
    } catch (error) {
      console.error('Error fetching users:', error);
      setMessage('Error loading users');
    }
  };

  const handleDocumentSelect = (doc) => {
    setSelectedDoc(doc);
    setSelectedUsers(doc.acl || []);
    setMessage('');
  };

  const handleUserToggle = (userEmail) => {
    if (selectedUsers.includes(userEmail)) {
      setSelectedUsers(selectedUsers.filter(u => u !== userEmail));
    } else {
      setSelectedUsers([...selectedUsers, userEmail]);
    }
  };

  const handleUpdateACL = async () => {
    if (!selectedDoc) {
      setMessage('Please select a document first');
      return;
    }

    setLoading(true);
    setMessage('');

    try {
      const response = await axios.post(
        'http://localhost:8000/admin/acl',
        {
          document_id: selectedDoc.document_id,
          acl: selectedUsers
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      setMessage(`✓ Updated access for ${response.data.updated_chunks} chunks`);
      
      // Refresh documents list
      await fetchDocuments();
      
      // Update selected doc with new ACL
      setSelectedDoc({
        ...selectedDoc,
        acl: selectedUsers
      });

    } catch (error) {
      console.error('Error updating ACL:', error);
      setMessage('✗ Error updating document access: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteDocument = async () => {
    if (!selectedDoc) {
      setMessage('Please select a document first');
      return;
    }

    if (!window.confirm(`Are you sure you want to delete "${selectedDoc.filename}"? This action cannot be undone.`)) {
      return;
    }

    setLoading(true);
    setMessage('');

    try {
      const response = await axios.delete(
        `http://localhost:8000/admin/document/${encodeURIComponent(selectedDoc.filename)}`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      setMessage(`✓ Deleted ${response.data.deleted_chunks} chunks and file`);
      
      // Clear selection
      setSelectedDoc(null);
      setSelectedUsers([]);
      
      // Refresh documents list
      await fetchDocuments();

    } catch (error) {
      console.error('Error deleting document:', error);
      setMessage('✗ Error deleting document: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-panel">
      <div className="admin-header">
        <h2>Document Access Control</h2>
        <button className="refresh-btn" onClick={fetchDocuments} title="Refresh documents list">
          ↻ Refresh
        </button>
      </div>
      
      <div className="admin-layout">
        {/* Documents List */}
        <div className="documents-section">
          <h3>Documents</h3>
          <div className="documents-list">
            {documents.length === 0 ? (
              <p className="empty-message">No documents found</p>
            ) : (
              documents.map((doc) => (
                <div
                  key={doc.document_id}
                  className={`document-item ${selectedDoc?.document_id === doc.document_id ? 'selected' : ''}`}
                  onClick={() => handleDocumentSelect(doc)}
                >
                  <div className="doc-name">{doc.filename}</div>
                  <div className="doc-acl">
                    {doc.acl && doc.acl.length > 0 ? (
                      <span className="acl-count">{doc.acl.length} user{doc.acl.length !== 1 ? 's' : ''}</span>
                    ) : (
                      <span className="acl-count no-access">No access granted</span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* ACL Editor */}
        <div className="acl-section">
          <h3>User Access</h3>
          
          {selectedDoc ? (
            <>
              <div className="selected-doc-info">
                <strong>Document:</strong> {selectedDoc.filename}
              </div>

              <div className="users-list">
                {users.map((user) => (
                  <label key={user.email} className="user-checkbox">
                    <input
                      type="checkbox"
                      checked={selectedUsers.includes(user.email)}
                      onChange={() => handleUserToggle(user.email)}
                    />
                    <span className="user-info">
                      <span className="user-name">{user.name}</span>
                      <span className="user-email">{user.email}</span>
                    </span>
                  </label>
                ))}
              </div>

              <div className="action-buttons">
                <button
                  className="update-btn"
                  onClick={handleUpdateACL}
                  disabled={loading}
                >
                  {loading ? 'Updating...' : 'Update Access'}
                </button>
                
                <button
                  className="delete-btn"
                  onClick={handleDeleteDocument}
                  disabled={loading}
                >
                  {loading ? 'Deleting...' : 'Delete Document'}
                </button>
              </div>

              {message && (
                <div className={`message ${message.startsWith('✓') ? 'success' : 'error'}`}>
                  {message}
                </div>
              )}
            </>
          ) : (
            <p className="empty-message">Select a document to manage access</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;
