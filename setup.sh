
#!/bin/bash

# RAG System Setup Script

echo "🔧 Setting up RAG System..."

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed!"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies!"
    exit 1
fi

# Create directories
echo "📁 Creating directories..."
mkdir -p data/chromadb
mkdir -p logs
mkdir -p models

# Make run script executable
chmod +x run.sh

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Download Llama 3 model:"
echo "   huggingface-cli download TheBloke/Llama-3-8B-Instruct-GGUF llama-3-8b-instruct.Q4_K_M.gguf --local-dir models --local-dir-use-symlinks False"
echo ""
echo "2. Start the server:"
echo "   ./run.sh"
echo ""
