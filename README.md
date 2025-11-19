# RAG System - Retrieval-Augmented Generation with Llama 3

A complete, production-ready RAG (Retrieval-Augmented Generation) system that allows you to upload documents (PDFs), scrape web content, and ask questions powered by Llama 3 and ChromaDB.

## 🌟 Features

- **📄 PDF Document Upload**: Upload and process PDF documents to extract text and create searchable embeddings
- **🌐 Web Scraping**: Extract and index content from web pages using BeautifulSoup
- **💬 Intelligent Q&A**: Ask questions and get accurate answers based on your indexed documents
- **🔍 Semantic Search**: Uses sentence-transformers for high-quality embeddings and ChromaDB for fast vector search
- **🤖 Llama 3 Integration**: Leverages open-source Llama 3 model for context-aware answer generation
- **🎨 Modern Web UI**: Clean, responsive interface for easy interaction
- **📊 Document Management**: View, manage, and delete indexed documents
- **⚡ Fast API**: Built with FastAPI for high performance

## 📋 Table of Contents

- [System Architecture](#system-architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Performance Optimization](#performance-optimization)
- [Contributing](#contributing)

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         RAG System                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────────┐  │
│  │   Frontend   │───▶│  FastAPI     │───▶│  RAG Pipeline   │  │
│  │ (HTML/JS/CSS)│    │   Backend    │    │                 │  │
│  └──────────────┘    └──────────────┘    └─────────────────┘  │
│                                                    │              │
│                            ┌───────────────────────┼──────────┐ │
│                            │                       │          │ │
│                       ┌────▼────┐          ┌──────▼──────┐   │ │
│                       │ChromaDB │          │  Llama 3    │   │ │
│                       │ Vector  │          │   Model     │   │ │
│                       │  Store  │          │ (llama-cpp) │   │ │
│                       └─────────┘          └─────────────┘   │ │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Components:

1. **Document Processing**
   - PDF text extraction (PyPDF2, pdfplumber)
   - Web scraping (BeautifulSoup, Requests)
   - Text chunking (LangChain RecursiveCharacterTextSplitter)

2. **Vector Store**
   - ChromaDB for persistent vector storage
   - Sentence-transformers for embeddings
   - Semantic similarity search

3. **LLM Integration**
   - Llama 3 via llama-cpp-python
   - Optimized for local deployment
   - GPU acceleration support

4. **API & Frontend**
   - FastAPI REST API
   - Modern, responsive web interface
   - Real-time statistics and document management

## 📦 Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2
- **Python**: 3.11 or higher
- **RAM**: Minimum 16GB (32GB recommended for better performance)
- **Storage**: At least 10GB free space for models and data
- **GPU** (Optional but recommended): NVIDIA GPU with 8GB+ VRAM for faster inference

### Software Requirements

- Python 3.11+
- pip package manager
- Git (for cloning)

## 🚀 Installation

### Step 1: Clone or Navigate to the Repository

```bash
cd /home/ubuntu/rag_system
```

### Step 2: Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Download Llama 3 Model

You need to download a Llama 3 model in GGUF format. Here are the recommended options:

#### Option A: Using Hugging Face CLI (Recommended)

```bash
# Install huggingface-cli if not already installed
pip install huggingface-hub[cli]

# Create models directory
mkdir -p models

# Download Llama 3 8B Instruct (Quantized Q4_K_M - ~4.9GB)
huggingface-cli download TheBloke/Llama-3-8B-Instruct-GGUF llama-3-8b-instruct.Q4_K_M.gguf --local-dir models --local-dir-use-symlinks False
```

#### Option B: Manual Download

1. Visit: https://huggingface.co/TheBloke/Llama-3-8B-Instruct-GGUF
2. Download `llama-3-8b-instruct.Q4_K_M.gguf` (or any other quantization)
3. Place the file in the `models/` directory

#### Model Options:

| Model Size | File Name | VRAM Required | Speed | Quality |
|------------|-----------|---------------|-------|---------|
| Q4_K_M (Recommended) | llama-3-8b-instruct.Q4_K_M.gguf | ~5GB | Fast | Good |
| Q5_K_M (Better Quality) | llama-3-8b-instruct.Q5_K_M.gguf | ~6GB | Medium | Better |
| Q8_0 (Best Quality) | llama-3-8b-instruct.Q8_0.gguf | ~9GB | Slower | Best |

### Step 5: Update Configuration (Optional)

Edit `config.yaml` to customize settings:

```yaml
llm:
  model_path: "./models/llama-3-8b-instruct.Q4_K_M.gguf"
  n_gpu_layers: 35  # Set to 0 if no GPU available
  n_threads: 8      # Adjust based on your CPU cores
```

## ⚙️ Configuration

The system uses `config.yaml` for configuration. Key settings:

### Application Settings
```yaml
app:
  host: "0.0.0.0"  # Listen on all interfaces
  port: 8000       # Port number
  debug: false     # Enable debug mode
```

### ChromaDB Settings
```yaml
chromadb:
  persist_directory: "./data/chromadb"  # Database location
  collection_name: "documents"          # Collection name
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
```

### LLM Settings
```yaml
llm:
  model_path: "./models/llama-3-8b-instruct.Q4_K_M.gguf"
  context_length: 4096   # Context window size
  max_tokens: 512        # Max tokens to generate
  temperature: 0.7       # Sampling temperature (0.0-1.0)
  n_gpu_layers: 35       # GPU layers (0 for CPU only)
```

### Text Processing Settings
```yaml
text_processing:
  chunk_size: 512        # Characters per chunk
  chunk_overlap: 100     # Overlap between chunks
```

### RAG Settings
```yaml
rag:
  retrieval_k: 5               # Number of chunks to retrieve
  relevance_threshold: 0.5     # Minimum relevance score
```

## 🏃 Running the Application

### Start the Server

```bash
# Make sure you're in the project directory with venv activated
cd /home/ubuntu/rag_system
source venv/bin/activate

# Run the server
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Alternative: Using Python directly

```bash
python backend/main.py
```

The server will start and be accessible at:
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/api/health

### First-Time Startup Notes:

1. **Model Loading**: The first startup will load the Llama 3 model into memory, which may take 30-60 seconds
2. **ChromaDB Initialization**: ChromaDB will create the database directory on first run
3. **Check Logs**: Monitor logs in `logs/rag_system.log` for any issues

## 📖 Usage Guide

### 1. Upload PDF Documents

1. Navigate to the **"Upload PDF"** tab
2. Click "Choose PDF Files" or drag & drop PDF files
3. Files will be processed automatically
4. You'll see confirmation with number of chunks created

### 2. Scrape Web Content

1. Navigate to the **"Scrape URL"** tab
2. Enter the URL of the web page
3. Click "Scrape & Index"
4. Content will be extracted and indexed

### 3. Ask Questions

1. Navigate to the **"Ask Questions"** tab
2. Enter your question in the text area
3. Optionally adjust the number of sources to retrieve
4. Click "Ask Question"
5. View the answer and source documents

**Keyboard Shortcuts**:
- `Ctrl/Cmd + Enter`: Submit query

### 4. Manage Documents

1. Navigate to the **"Manage Documents"** tab
2. View all indexed documents grouped by source
3. Delete specific sources or clear all documents

### Example Queries

After uploading documents, try these types of questions:

- "What is the main topic discussed in the documents?"
- "Summarize the key points about [specific topic]"
- "What are the recommendations mentioned?"
- "Who are the key people or organizations mentioned?"
- "What dates or deadlines are mentioned?"

## 🔌 API Documentation

### Base URL: `http://localhost:8000/api`

### Endpoints

#### 1. Health Check
```
GET /api/health
```
Returns system health status.

#### 2. Upload PDF
```
POST /api/upload-pdf
Content-Type: multipart/form-data

Body:
- file: PDF file
```

#### 3. Scrape URL
```
POST /api/scrape-url
Content-Type: application/json

{
  "url": "https://example.com/page"
}
```

#### 4. Query
```
POST /api/query
Content-Type: application/json

{
  "question": "What is RAG?",
  "n_results": 5,
  "return_sources": true
}
```

#### 5. Get Documents
```
GET /api/documents
```

#### 6. Delete Document
```
DELETE /api/documents/{document_id}
```

#### 7. Delete Source
```
DELETE /api/documents/source/{source_name}
```

#### 8. Get Statistics
```
GET /api/stats
```

#### 9. Clear All Documents
```
DELETE /api/clear
```

### Interactive API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation.

## 🐛 Troubleshooting

### Common Issues

#### 1. Model Not Found Error

**Error**: `FileNotFoundError: Model file not found`

**Solution**:
```bash
# Download the model
cd /home/ubuntu/rag_system
mkdir -p models
huggingface-cli download TheBloke/Llama-3-8B-Instruct-GGUF llama-3-8b-instruct.Q4_K_M.gguf --local-dir models --local-dir-use-symlinks False
```

#### 2. Out of Memory Error

**Error**: `RuntimeError: CUDA out of memory` or system hangs

**Solution**:
- Use a smaller quantized model (Q4_K_M instead of Q8_0)
- Reduce `n_gpu_layers` in config.yaml (try 20, 10, or 0)
- Reduce `context_length` to 2048
- Close other applications

#### 3. Slow Response Times

**Solutions**:
- Enable GPU: Set `n_gpu_layers: 35` in config.yaml
- Use CPU efficiently: Set `n_threads` to your CPU core count
- Use smaller models: Q4_K_M is faster than Q8_0
- Reduce `retrieval_k` to 3 instead of 5

#### 4. ChromaDB Lock Error

**Error**: `sqlite3.OperationalError: database is locked`

**Solution**:
```bash
# Stop all running instances
pkill -f "uvicorn"

# Remove lock files
rm -f data/chromadb/*.lock
```

#### 5. PDF Extraction Failed

**Error**: No text extracted from PDF

**Solution**:
- PDF might be image-based (scanned)
- Try a different PDF
- Check if PDF is password protected

#### 6. Import Errors

**Error**: `ModuleNotFoundError`

**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Checking Logs

View detailed logs:
```bash
tail -f logs/rag_system.log
```

## ⚡ Performance Optimization

### GPU Acceleration

If you have an NVIDIA GPU with CUDA:

```bash
# Install CUDA-enabled llama-cpp-python
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --force-reinstall --no-cache-dir

# Update config.yaml
llm:
  n_gpu_layers: 35  # Load most layers on GPU
```

### CPU Optimization

```yaml
llm:
  n_gpu_layers: 0        # CPU only
  n_threads: 8           # Match your CPU cores
  n_batch: 512           # Batch size
```

### Memory Optimization

1. Use quantized models (Q4_K_M is 60% smaller than Q8_0)
2. Reduce context length: `context_length: 2048`
3. Reduce chunk retrieval: `retrieval_k: 3`

### Storage Optimization

ChromaDB data is stored in `data/chromadb/`. To manage storage:

```bash
# Check size
du -sh data/chromadb/

# Backup before clearing
tar -czf chromadb_backup.tar.gz data/chromadb/

# Clear old data through the API or UI
```

## 🔒 Security Considerations

### For Production Deployment:

1. **Change Default Host**:
   ```yaml
   app:
     host: "127.0.0.1"  # Only local access
   ```

2. **Add Authentication**: Implement API key authentication in routes.py

3. **HTTPS**: Use a reverse proxy (nginx) with SSL

4. **File Upload Limits**: Already configured with FastAPI, but review for your needs

5. **Input Validation**: Built-in with Pydantic models

## 📝 Project Structure

```
rag_system/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── models.py          # Pydantic models
│   │   └── routes.py          # API endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── llm.py             # LLM integration
│   │   ├── rag_pipeline.py    # RAG orchestration
│   │   └── vector_store.py    # ChromaDB interface
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── document_processor.py  # PDF & text processing
│   │   ├── logger.py              # Logging setup
│   │   └── web_scraper.py         # Web scraping
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   └── main.py                # FastAPI application
├── frontend/
│   ├── index.html             # Web interface
│   ├── style.css              # Styles
│   └── app.js                 # Frontend logic
├── data/
│   └── chromadb/              # Vector database (created on first run)
├── logs/
│   └── rag_system.log         # Application logs
├── models/
│   └── [llama model].gguf     # LLM model (download separately)
├── config.yaml                # Configuration file
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Add support for more document formats (DOCX, TXT, etc.)
- Implement user authentication
- Add conversation history
- Improve web scraping for JavaScript-heavy sites
- Add multi-language support
- Implement caching for common queries

## 📄 License

This project is open-source. Please ensure compliance with Llama 3 license terms when using the model.

## 🙏 Acknowledgments

- **Llama 3**: Meta AI's open-source language model
- **ChromaDB**: Vector database for embeddings
- **LangChain**: Text processing utilities
- **FastAPI**: High-performance web framework
- **Sentence Transformers**: Embedding models

## 📞 Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review logs in `logs/rag_system.log`
3. Check API documentation at `/docs`

## 🔄 Updates and Maintenance

### Updating Dependencies

```bash
pip install --upgrade -r requirements.txt
```

### Updating Models

Download newer versions of Llama models as they become available and update `config.yaml`.

### Database Maintenance

```bash
# Backup database
tar -czf chromadb_backup_$(date +%Y%m%d).tar.gz data/chromadb/

# Restore database
tar -xzf chromadb_backup_YYYYMMDD.tar.gz
```

---

**Enjoy using your RAG System! 🚀**
