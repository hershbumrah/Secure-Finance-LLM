# Secure Finance LLM

A secure, role-based access control (RBAC) system for querying financial documents using Large Language Models with vector search capabilities.

## Project Structure

```
secure-finance-llm/
│
├── backend/                 # FastAPI backend service
│   ├── main.py             # API server entry point
│   ├── auth.py             # JWT validation + RBAC
│   ├── retriever.py        # ACL-filtered document retrieval
│   ├── guardrails.py       # Hallucination prevention
│   ├── logging.py          # Audit logging
│   └── prompts.py          # LLM instruction templates
│
├── indexer/                # Document processing pipeline
│   ├── ingest_pdfs.py      # PDF chunking + metadata tagging
│   └── upsert_qdrant.py    # Embedding + vector DB insertion
│
├── vector_db/              # Vector database setup
│   └── docker-compose.yml  # Qdrant local deployment
│
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── App.jsx         # Main application component
│   │   ├── components/     # UI components
│   │   │   ├── QueryInput.jsx
│   │   │   ├── ResponseDisplay.jsx
│   │   │   └── Login.jsx
│   │   └── api.js          # API wrapper
│   └── package.json
│
└── infra/                  # Infrastructure configuration
    ├── docker/             # Docker container configs
    │   ├── Dockerfile.backend
    │   ├── Dockerfile.frontend
    │   └── docker-compose.yml
    └── k8s/                # Kubernetes manifests
        ├── namespace.yaml
        ├── qdrant-deployment.yaml
        ├── backend-deployment.yaml
        └── frontend-deployment.yaml
```

## Features

- **Secure Authentication**: JWT-based authentication with role-based access control
- **Document Security**: ACL-filtered document retrieval ensuring users only access authorized content
- **Hallucination Prevention**: Guardrails to validate LLM responses against source documents
- **Audit Logging**: Comprehensive logging for compliance and monitoring
- **Vector Search**: Semantic search using Qdrant vector database
- **Modern UI**: React-based frontend with intuitive query interface

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the API server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Vector Database Setup

1. Navigate to the vector_db directory:
```bash
cd vector_db
```

2. Start Qdrant using Docker Compose:
```bash
docker-compose up -d
```

Qdrant will be available at:
- REST API: `http://localhost:6333`
- gRPC API: `http://localhost:6334`

### Document Indexing

1. Prepare your PDF documents in a directory
2. Run the ingestion pipeline:
```bash
cd indexer
python ingest_pdfs.py
python upsert_qdrant.py
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## Docker Deployment

### Using Docker Compose

Build and run all services:
```bash
cd infra/docker
docker-compose up --build
```

This will start:
- Qdrant on port 6333
- Backend API on port 8000
- Frontend on port 3000

## Kubernetes Deployment

1. Apply the namespace:
```bash
kubectl apply -f infra/k8s/namespace.yaml
```

2. Deploy services:
```bash
kubectl apply -f infra/k8s/qdrant-deployment.yaml
kubectl apply -f infra/k8s/backend-deployment.yaml
kubectl apply -f infra/k8s/frontend-deployment.yaml
```

3. Check deployment status:
```bash
kubectl get pods -n secure-finance-llm
```

## Configuration

### Backend Environment Variables

- `QDRANT_HOST`: Qdrant server hostname (default: localhost)
- `QDRANT_PORT`: Qdrant server port (default: 6333)
- `SECRET_KEY`: JWT secret key (change in production!)

### Frontend Environment Variables

- `REACT_APP_API_URL`: Backend API URL (default: http://localhost:8000)

## Security Considerations

1. **Change Default Secrets**: Update `SECRET_KEY` in production
2. **HTTPS**: Use HTTPS in production environments
3. **CORS**: Configure CORS appropriately for your domain
4. **ACL Mapping**: Ensure proper ACL configuration for document access
5. **Input Validation**: All inputs are validated before processing

## API Documentation

Once the backend is running, visit:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Development

### Backend Dependencies

Key dependencies (add to `requirements.txt`):
- fastapi
- uvicorn
- pydantic
- python-jose[cryptography]
- python-multipart
- qdrant-client

### Frontend Dependencies

Included in `package.json`:
- react
- react-dom
- axios

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Support

[Add support contact information here]
