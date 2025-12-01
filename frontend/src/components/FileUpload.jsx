import React, { useState } from 'react';
import './FileUpload.css';
import { uploadPDF } from '../api';

function FileUpload({ token }) {
  const [file, setFile] = useState(null);
  const [acl, setAcl] = useState('');
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setError(null);
    } else {
      setFile(null);
      setError('Please select a PDF file');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setError(null);
    setMessage(null);

    try {
      const result = await uploadPDF(file, acl, token);
      setMessage(result.message || 'File uploaded successfully!');
      setFile(null);
      setAcl('');
      // Reset file input
      e.target.reset();
    } catch (err) {
      setError(err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="file-upload-container">
      <h3>Upload PDF Document</h3>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="pdf-file">Select PDF File</label>
          <input
            type="file"
            id="pdf-file"
            accept="application/pdf"
            onChange={handleFileChange}
            disabled={uploading}
          />
          {file && <div className="file-name">Selected: {file.name}</div>}
        </div>

        <div className="form-group">
          <label htmlFor="acl">Access Control (User IDs)</label>
          <input
            type="text"
            id="acl"
            placeholder="user1, user2, user3"
            value={acl}
            onChange={(e) => setAcl(e.target.value)}
            disabled={uploading}
          />
          <small>Comma-separated list of users who can access this document</small>
        </div>

        <button
          type="submit"
          className="upload-btn"
          disabled={uploading || !file}
        >
          {uploading ? 'Uploading...' : 'Upload'}
        </button>
      </form>

      {message && <div className="success-message">{message}</div>}
      {error && <div className="error-message">{error}</div>}
    </div>
  );
}

export default FileUpload;
