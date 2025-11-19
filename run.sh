
#!/bin/bash

# RAG System Startup Script

echo "🚀 Starting RAG System..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if model exists
if [ ! -f "models/llama-3-8b-instruct.Q4_K_M.gguf" ]; then
    echo "⚠️  Warning: Llama 3 model not found in models/ directory"
    echo "Please download the model using:"
    echo "  huggingface-cli download TheBloke/Llama-3-8B-Instruct-GGUF llama-3-8b-instruct.Q4_K_M.gguf --local-dir models --local-dir-use-symlinks False"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create necessary directories
mkdir -p data/chromadb
mkdir -p logs

# Start the server
echo "🌐 Starting server on http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "Press Ctrl+C to stop"
echo ""

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
