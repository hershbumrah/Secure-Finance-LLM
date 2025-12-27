# Secure Finance LLM 🔐

A production-ready RAG (Retrieval-Augmented Generation) system for secure financial document querying. Built with FastAPI, Ollama, and Qdrant vector database, featuring JWT authentication, role-based access control, automatic document indexing, and a modern dark-themed UI.

> **⚠️ SECURITY WARNING:** This project contains sensitive configurations. Before deploying or pushing to GitHub:
> 1. ✅ Copy `.env.example` to `.env` and set your own `JWT_SECRET`
> 2. ✅ Never commit `.env` files to git
> 3. ✅ Review `GITHUB_SETUP.md` for deployment best practices
> 4. ✅ Read `DEPLOYMENT.md` for production security guidelines

---

## ✨ Features

### Core Functionality
- **🔐 Enterprise Security**: JWT authentication with role-based access control (RBAC)
- **📄 Document Intelligence**: Vector-based semantic search with ACL filtering per document
- **🤖 Local LLM Integration**: Ollama-powered responses (llama3) with source citation tracking
- **🛡️ AI Guardrails**: Hallucination prevention, PII detection, and response validation
- **📊 Audit Compliance**: Comprehensive logging for regulatory requirements
- **⚡ Modern Stack**: FastAPI backend, React frontend, containerized deployment

### Advanced Features
- **🚀 Automatic Indexing**: PDFs are automatically indexed upon upload (no manual indexing needed)
- **🎯 Document-Specific Queries**: Filter queries to specific documents via dropdown selector
- **♻️ Re-upload Support**: Automatically cleans up old chunks and re-indexes when you re-upload files
- **🗑️ Document Deletion**: Delete PDFs and all their chunks through the admin panel
- **👥 Admin Panel**: Manage document permissions with checkbox UI for user access control
- **🔄 Permission Updates**: Bulk update ACLs across all chunks of a document
- **📑 Smart Retrieval**: Diversity algorithm retrieves 10 chunks from multiple documents for better context
- **📝 Large Chunks**: 100-word text chunks (up from 50) for comprehensive answers
- **🎨 Dark Theme UI**: Professional black/dark gray backgrounds with silver metallic accents
- **🔍 Source Deduplication**: Clean source lists without duplicate filenames
- **📊 Chunk Awareness**: LLM knows the difference between text chunks and actual document count

---

## 📋 Table of Contents

- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start Guide](#quick-start-guide)
- [Complete User Guide](#complete-user-guide)
- [API Endpoints](#api-endpoints)
- [Admin Panel Features](#admin-panel-features)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Security Best Practices](#security-best-practices)
- [Troubleshooting](#troubleshooting)

---

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   React     │─────▶│   FastAPI    │─────▶│   Qdrant    │
│  Frontend   │      │   Backend    │      │  Vector DB  │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │    Ollama    │
                     │  LLM Server  │
                     └──────────────┘
```

## Project Structure

```
secure-finance-llm/
│
├── backend/                     # FastAPI backend service
│   ├── main.py                 # API server with all endpoints
│   ├── auth.py                 # JWT validation and RBAC
│   ├── retriever.py            # ACL-filtered vector search with diversity
│   ├── guardrails.py           # Response validation and PII detection
│   ├── audit_logging.py        # Compliance logging
│   ├── llm_client.py           # Ollama integration with langchain
│   ├── prompts.py              # LLM prompt templates
│   ├── indexer_service.py      # Automatic PDF indexing on upload
│   ├── clear_qdrant.py         # Utility to clear vector database
│   └── pyproject.toml          # Python dependencies
│
├── indexer/                    # Manual document processing (optional)
│   ├── ingest_pdfs.py          # PDF chunking with metadata
│   ├── stream_index.py         # Memory-efficient streaming indexer
│   └── upsert_qdrant.py        # Vector embedding and insertion
│
├── vector_db/                  # Vector database setup
│   └── docker-compose.yml      # Qdrant local deployment
│
├── data/                       # Data storage
│   ├── pdfs/                   # Uploaded PDF documents
│   └── README.md               # Data directory documentation
│
├── frontend/                   # React frontend application
│   ├── src/
│   │   ├── App.jsx             # Main app with navigation
│   │   ├── api.js              # API client functions
│   │   └── components/         # UI components
│   │       ├── Login.jsx       # JWT authentication
│   │       ├── QueryInput.jsx  # Query interface with document filter
│   │       ├── ResponseDisplay.jsx  # Answer display with sources
│   │       ├── FileUpload.jsx  # PDF upload with auto-indexing
│   │       └── AdminPanel.jsx  # Document & permission management
│   └── package.json
│
├── infra/                      # Infrastructure as Code
│   ├── docker/                 # Container configurations
│   └── k8s/                    # Kubernetes manifests
│
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore patterns
├── LICENSE                     # MIT License
├── README.md                   # This file
├── DEPLOYMENT.md               # Production deployment guide
├── NEW_FEATURES.md             # Feature changelog
```

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+** - [Download](https://www.python.org/downloads/)
- **uv** (Python package manager) - [Install guide](https://github.com/astral-sh/uv)
  ```bash
  # macOS/Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh
  
  # Windows
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- **Node.js 18+** and npm - [Download](https://nodejs.org/)
- **Docker Desktop** - [Download](https://www.docker.com/products/docker-desktop)
- **Ollama** - [Download](https://ollama.ai)
  ```bash
  # macOS
  brew install ollama
  
  # Linux
  curl -fsSL https://ollama.com/install.sh | sh
  
  # Windows - download from website
  ```

---

## Quick Start Guide

**For first-time users**, follow these steps to get up and running in 10 minutes:

### Step 1: Clone the Repository

```bash
git clone https://github.com/hershbumrah/Secure-Finance-LLM.git
cd Secure-Finance-LLM
```

### Step 2: Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Generate a secure JWT secret
openssl rand -hex 32

# Edit .env and paste your generated secret
nano .env  # or use any text editor
```

**In `.env`, update these values:**
```env
JWT_SECRET=paste-your-generated-secret-here
LLM_MODEL=llama3
LLM_BASE_URL=http://localhost:11434
EMBEDDING_MODEL=all-minilm
```

### Step 3: Start Qdrant Vector Database

```bash
cd vector_db
docker-compose up -d
cd ..
```

✅ Verify Qdrant is running: Open http://localhost:6333 in your browser

### Step 4: Install and Start Ollama

```bash
# Start Ollama (if not already running)
ollama serve

# In a new terminal, pull required models
ollama pull llama3
ollama pull all-minilm
```

✅ Verify Ollama: `ollama list` should show both models

### Step 5: Start the Backend

```bash
cd backend
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install fastapi uvicorn python-jose[cryptography] python-multipart \
  qdrant-client langchain-community pypdf2 python-dotenv ollama

# Start the server
python main.py
```

✅ Backend running at: http://localhost:8000
✅ Test it: http://localhost:8000/health

### Step 6: Start the Frontend

```bash
# In a new terminal
cd frontend
npm install
npm start
```

✅ Frontend running at: http://localhost:3000

### Step 7: Log In

Open http://localhost:3000 in your browser:
- **Username**: `admin` (or any name)
- **Password**: (any password - demo mode accepts all)
- **Role**: All users get admin role by default for demo

🎉 **You're ready to use the application!**

---

## Complete User Guide

### 📤 Uploading Documents

1. **Navigate to "Query Documents"** tab (default view)
2. Click **"Choose File"** in the upload section
3. Select a PDF file (max 50MB)
4. Click **"Upload"**
5. ⏳ Wait for "File uploaded successfully" message
6. 🎯 **Document is automatically indexed in the background** (no manual indexing needed!)

**Supported formats:** PDF only

**What happens behind the scenes:**
- PDF is saved to `data/pdfs/`
- Background task chunks the document into 100-word segments
- Each chunk is embedded using `all-minilm` model
- Vectors are stored in Qdrant with metadata (filename, page number, chunk index)
- You can immediately query the document after upload completes

### 🔍 Querying Documents

#### Basic Query (All Documents)

1. In the **document filter dropdown**, ensure **"All Documents"** is selected
2. Type your question in the text area:
   ```
   What were the key findings in the financial reports?
   ```
3. Click **"Submit Query"**
4. View the comprehensive answer with source citations

#### Query Specific Document

1. Use the **document filter dropdown** to select a specific PDF
2. Type your question - it will only search that document
3. Submit and view results

**Tips for better queries:**
- Be specific: "What was Q4 revenue?" vs "Tell me about revenue"
- Ask for details: "Explain the risk factors mentioned in section 3"
- Reference context: "Compare the 2023 and 2024 performance"

**The system returns:**
- Comprehensive answer synthesized from 10 text chunks
- Source files with filenames
- Retrieval uses diversity algorithm (chunks from multiple documents when possible)

### 👨‍💼 Admin Panel Features

Click **"Manage Access (Admin)"** tab to access admin features.

#### 📋 View All Documents

- See all uploaded PDFs with their filenames
- View number of users with access to each document
- Click **"Refresh Documents"** to reload the list

#### 🔐 Manage Document Permissions

1. **Select a document** from the list
2. **Check/uncheck users** who should have access
3. Click **"Update Access"**
4. ✅ Permissions updated across all chunks of that document

**How ACLs work:**
- Each document chunk stores an ACL list in its metadata
- When a user queries, only chunks they have access to are returned
- Admins bypass ACL filters and see everything

#### 🗑️ Delete Documents

1. Select a document
2. Click **"Delete Document"** (red button)
3. Confirm deletion in the dialog
4. Document is removed from:
   - Qdrant vector database (all chunks)
   - File system (`data/pdfs/`)

#### ♻️ Re-uploading Documents

If you upload a file that already exists:
- Old chunks are automatically deleted from Qdrant
- File is overwritten on disk
- Fresh indexing begins with new chunks
- **Perfect for updating documents with new versions**

### 📊 Understanding Query Results

**Answer Section:**
- Comprehensive response synthesized from retrieved chunks
- The LLM knows it's seeing N chunks from M documents
- Response includes specific details and examples from sources

**Sources Section:**
- Lists unique filenames (deduplicated automatically)
- Shows which documents were used to generate the answer

**Note on chunk count:**
- System retrieves 10 chunks internally for better context
- But tells the LLM the actual number of unique documents
- Example: "You are seeing 10 text excerpts from 5 source documents"

### 🎨 UI Features

- **Dark Theme**: Professional black/gray backgrounds
- **Silver Accents**: Metallic silver borders and highlights
- **Responsive Design**: Works on desktop and tablets
- **Hover Effects**: Buttons and cards have smooth animations
- **Loading States**: Visual feedback during processing

---

## API Endpoints

### Authentication

#### POST `/auth/login`
Generate JWT token for authentication.

**Request:**
```json
{
  "username": "admin",
  "password": "anypassword"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": "admin",
  "role": "admin"
}
```

### Document Operations

#### POST `/upload`
Upload and automatically index a PDF document.

**Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Form Data:**
- `file`: PDF file (multipart/form-data)
- `acl`: JSON array of user IDs (optional)

**Response:**
```json
{
  "filename": "report.pdf",
  "size": 1024000,
  "status": "success",
  "message": "Document indexing started in background"
}
```

#### GET `/admin/documents`
List all uploaded documents with ACL info.

**Response:**
```json
{
  "documents": [
    {
      "filename": "report.pdf",
      "document_id": "abc123",
      "acl_count": 3
    }
  ]
}
```

#### POST `/admin/acl`
Update document access permissions.

**Request:**
```json
{
  "document_id": "abc123",
  "acl": ["user1@example.com", "user2@example.com"]
}
```

#### DELETE `/admin/document/{filename}`
Delete document and all its chunks.

**Response:**
```json
{
  "status": "success",
  "deleted_chunks": 45,
  "filename": "report.pdf"
}
```

### Query Operations

#### POST `/query`
Query documents with RAG pipeline.

**Request:**
```json
{
  "query": "What is the revenue forecast?",
  "filters": {
    "source_file": "Q4-report.pdf"  // Optional: filter to specific document
  }
}
```

**Response:**
```json
{
  "answer": "Based on the financial reports...",
  "sources": [
    {
      "filename": "Q4-report.pdf",
      "page": 5
    }
  ],
  "confidence": 0.89
}
```

### Health Checks

#### GET `/health`
Service health status.

#### GET `/health/llm`
Test LLM connectivity and response.

---

## Admin Panel Features

### User Management

Currently using hardcoded users (demo mode). To integrate with your user database:

1. Edit `backend/main.py` - `list_users()` endpoint
2. Replace hardcoded list with database query
3. Update authentication logic in `auth.py`

### Document Access Control

**Three-level hierarchy:**
1. **Admin role**: Bypasses all ACL filters, sees everything
2. **User role**: Only sees documents in their ACL
3. **Document-level ACL**: Stored per chunk, updated in bulk

---

## Configuration

### Environment Variables

All sensitive configuration should be in `.env`:

```env
# LLM Configuration
LLM_MODEL=llama3                      # Ollama model name
LLM_BASE_URL=http://localhost:11434  # Ollama server URL
EMBEDDING_MODEL=all-minilm            # Embedding model

# JWT Authentication
JWT_SECRET=your-secret-key-here       # CHANGE THIS!
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Qdrant Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=finance_documents

# Backend API
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
CORS_ORIGINS=http://localhost:3000

# Storage
PDF_STORAGE_PATH=data/pdfs
MAX_FILE_SIZE_MB=50
```

### Retriever Configuration

Edit `backend/retriever.py` to adjust search behavior:

```python
# Number of chunks to retrieve
limit = 10  # Default: 10, increase for more context

# Diversity multiplier (retrieves limit * 3 initially)
results = client.query_points(limit=limit * 3)
```

### LLM Configuration

Edit `backend/llm_client.py` for model settings:

```python
# Temperature (0.0 = deterministic, 1.0 = creative)
ChatOllama(temperature=0.0)

# Different model
LLM_MODEL = "llama3.1"  # or "mistral", "codellama", etc.
```

### Chunk Size Configuration

Edit `backend/indexer_service.py`:

```python
CHUNK_SIZE = 100  # words per chunk (default: 100)
CHUNK_OVERLAP = 20  # overlap between chunks
```

---

## Deployment

### Local Development

Already covered in [Quick Start](#quick-start-guide) above.

### Docker Deployment

See detailed guide in `DEPLOYMENT.md` for:
- Full-stack Docker Compose setup
- Cloud deployment options (AWS, GCP, Azure, DigitalOcean)
- Kubernetes manifests
- Production security configurations
- Cost estimates

**Quick Docker start:**
```bash
docker-compose -f infra/docker/docker-compose.yml up -d
```
---

## Security Best Practices

### Before Going to Production

1. **Generate Strong JWT Secret**
   ```bash
   openssl rand -hex 32
   ```
   Update `.env` with this value

2. **Enable HTTPS**
   - Use Let's Encrypt for free SSL certificates
   - Configure reverse proxy (nginx recommended)

3. **Configure CORS Properly**
   ```python
   # In backend/main.py
   origins = [
       "https://yourdomain.com",  # Your production domain only
   ]
   ```

4. **Implement Rate Limiting**
   ```bash
   pip install slowapi
   ```

5. **Set Up Authentication Database**
   - Replace hardcoded demo users
   - Use proper password hashing (bcrypt)
   - Implement password policies

6. **Enable Audit Logging**
   - Logs stored in `backend/logs/audit.log`
   - Monitor for suspicious activity
   - Rotate logs regularly

7. **Scan for Vulnerabilities**
   ```bash
   # Run before pushing to GitHub
   ./check-security.sh
   ```

8. **Update Dependencies Regularly**
   ```bash
   uv pip list --outdated
   npm audit fix
   ```

### Security Checklist

- [ ] JWT_SECRET changed from default
- [ ] .env files not committed to git
- [ ] HTTPS enabled in production
- [ ] CORS restricted to your domain
- [ ] File upload size limits enforced
- [ ] PDF validation enabled
- [ ] Rate limiting configured
- [ ] Audit logs monitored
- [ ] Dependencies up to date
- [ ] Qdrant authentication enabled (production)

---

## Troubleshooting

### Common Issues and Solutions

#### 1. "Ollama connection failed"

**Problem:** Backend can't connect to Ollama

**Solutions:**
```bash
# Check if Ollama is running
ollama list

# Start Ollama server
ollama serve

# Verify models are installed
ollama pull llama3
ollama pull all-minilm

# Test connection
curl http://localhost:11434/api/tags
```

#### 2. "Qdrant connection refused"

**Problem:** Vector database not accessible

**Solutions:**
```bash
# Check if Qdrant container is running
docker ps | grep qdrant

# Restart Qdrant
cd vector_db
docker-compose restart

# Check logs
docker-compose logs qdrant

# Verify it's accessible
curl http://localhost:6333/collections
```

#### 3. "No documents found after upload"

**Problem:** PDF uploaded but not indexed

**Solutions:**
```bash
# Check backend logs
cd backend
tail -f logs/*.log

# Verify PDF is in data/pdfs/
ls -lh ../data/pdfs/

# Check Qdrant has data
curl http://localhost:6333/collections/finance_documents
```

#### 4. "CORS error in browser console"

**Problem:** Frontend can't call backend API

**Solutions:**
```python
# In backend/main.py, ensure frontend URL is in CORS origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 5. "JWT token expired"

**Problem:** Authentication token no longer valid

**Solution:**
- Log out and log back in
- Tokens expire after 24 hours by default
- Change `JWT_EXPIRATION_HOURS` in .env to increase

#### 6. "Empty or vague LLM responses"

**Problem:** Answers are too short or lack detail

**Solutions:**
- Increase chunk size in `indexer_service.py` (already set to 100 words)
- Increase retrieval limit in `retriever.py` (already set to 10)
- Make queries more specific
- Ensure documents are properly indexed
- Check if LLM model needs more context

#### 7. "File upload rejected"

**Problem:** Can't upload PDF files

**Solutions:**
```python
# Check file size limit in backend/main.py
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Ensure data/pdfs/ directory exists
mkdir -p data/pdfs

# Check file permissions
chmod 755 data/pdfs
```

### Debug Mode

Enable detailed logging:

```python
# In backend/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check logs:
```bash
# Backend logs
tail -f backend/logs/*.log

# Docker logs (if using Docker)
docker-compose logs -f backend
```

### Performance Issues

If queries are slow:

1. **Check Qdrant performance**
   ```bash
   curl http://localhost:6333/collections/finance_documents
   # Look at "vectors_count" and "indexed_vectors_count"
   ```

2. **Reduce retrieval limit**
   - Edit `backend/retriever.py`
   - Change `limit=10` to `limit=5`

3. **Use GPU for Ollama**
   ```bash
   # Install CUDA version of Ollama
   # Or use smaller models: mistral, phi
   ```

4. **Optimize chunk size**
   - Smaller chunks = faster search but less context
   - Larger chunks = slower but better answers
   - Current: 100 words (good balance)

### Getting Help

1. **Check existing issues**: [GitHub Issues](https://github.com/hershbumrah/Secure-Finance-LLM/issues)
2. **Read documentation**: `DEPLOYMENT.md`, `GITHUB_SETUP.md`
3. **View logs**: `backend/logs/` directory
4. **Run security check**: `./check-security.sh`
5. **Open a new issue**: Provide logs, error messages, and steps to reproduce

---

## Development

### Backend Stack
- **FastAPI** - Modern async web framework with automatic API docs
- **Ollama** - Local LLM inference (llama3 for generation, all-minilm for embeddings)
- **Qdrant** - Vector similarity search with filtering
- **langchain-community** - LLM orchestration and abstractions
- **PyJWT** - JWT token authentication
- **PyPDF2** - PDF text extraction

### Frontend Stack
- **React 18** - UI framework with hooks
- **Axios** - HTTP client for API calls
- **CSS3** - Custom styling with dark theme

### Project Architecture

**RAG Pipeline Flow:**
1. User uploads PDF → `indexer_service.py`
2. PDF chunked into 100-word segments → `PyPDF2`
3. Chunks embedded → `all-minilm` model via Ollama
4. Vectors stored in Qdrant with metadata → `qdrant-client`
5. User queries → `retriever.py` searches Qdrant
6. Top 10 chunks retrieved (with diversity) → `backend/retriever.py`
7. Chunks sent to LLM with prompt → `llm_client.py`
8. LLM generates answer → `llama3` via Ollama
9. Response validated → `guardrails.py`
10. Answer + sources returned to frontend

### Running Tests

```bash
# Backend API test
curl http://localhost:8000/health

# LLM test
curl http://localhost:8000/health/llm

# Auth test
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'

# Query test (requires token)
curl -X POST http://localhost:8000/query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is this about?"}'
```

### Adding New Features

1. **Backend endpoint**: Add to `backend/main.py`
2. **Frontend component**: Add to `frontend/src/components/`
3. **API call**: Add to `frontend/src/api.js`
4. **Update UI**: Import and use in `App.jsx`

---

## Performance Tuning

### Embedding Optimization
- **Batch size**: Process multiple chunks at once
- **Model choice**: `all-minilm` is fast but small, alternatives: `bge-large`, `e5-large`

### Search Optimization
- **Limit**: Currently 10, reduce to 5-7 for faster queries
- **Diversity**: Disable if you want most relevant chunks only
- **Filters**: Use document-specific queries when possible

### LLM Optimization
- **Model choice**: `llama3` (8B) is balanced, alternatives: `mistral` (7B, faster), `llama3.1` (larger, slower)
- **Temperature**: Set to 0.0 for deterministic responses
- **Context window**: Adjust max tokens if needed

### Vector Database
- **Indexing**: Qdrant auto-indexes, but you can tune in production
- **Quantization**: Enable for larger datasets to save memory
- **Replication**: Set up for high availability

---

## Contributing

We welcome contributions! Here's how:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Test thoroughly**
5. **Run security check**
   ```bash
   ./check-security.sh
   ```
6. **Commit with clear message**
   ```bash
   git commit -m "Add: feature description"
   ```
7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Open a Pull Request**

### Contribution Guidelines

- Follow existing code style
- Add comments for complex logic
- Update README if adding features
- Test locally before submitting PR
- Don't commit secrets or .env files

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

You are free to:
- ✅ Use commercially
- ✅ Modify
- ✅ Distribute
- ✅ Use privately

---

## Acknowledgments

Built with amazing open-source tools:

- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Ollama](https://ollama.ai/) - Local LLM runtime
- [Qdrant](https://qdrant.tech/) - Vector database
- [LangChain](https://www.langchain.com/) - LLM framework
- [React](https://react.dev/) - Frontend framework

Special thanks to the open-source community! 🙏

---

## Roadmap

Future enhancements planned:

- [ ] Multi-user authentication with database
- [ ] Support for Word, Excel, PowerPoint files
- [ ] Conversation history and context
- [ ] Export query results to PDF
- [ ] API key authentication for programmatic access
- [ ] Advanced search filters (date ranges, document types)
- [ ] Document comparison feature
- [ ] Batch document upload
- [ ] Custom embedding models
- [ ] Multi-language support

---

## Support

- 📖 **Documentation**: Read `DEPLOYMENT.md` and `GITHUB_SETUP.md`
- 🐛 **Bug Reports**: [Open an issue](https://github.com/hershbumrah/Secure-Finance-LLM/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/hershbumrah/Secure-Finance-LLM/discussions)
- 📧 **Contact**: Create an issue or discussion

---

**Made with ❤️ for the open-source community**
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Ollama](https://ollama.ai/) - Local LLM runtime
- [Qdrant](https://qdrant.tech/) - Vector database
- [LangChain](https://langchain.com/) - LLM orchestration

## Contact

For questions or support, open an issue on GitHub.
