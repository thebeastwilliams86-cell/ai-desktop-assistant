#!/bin/bash

# AI Desktop Assistant Installation Script
# This script installs dependencies and sets up the AI Desktop Assistant

echo "🤖 AI Desktop Assistant Installation"
echo "===================================="

# Check Python version
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
if [[ $(echo "$python_version >= 3.7" | bc -l) -eq 0 ]]; then
    echo "❌ Error: Python 3.7 or higher is required. Found version $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is not installed"
    exit 1
fi

echo "✅ pip3 is installed"

# Create virtual environment (optional but recommended)
read -p "📦 Create virtual environment? (recommended) [Y/n]: " create_venv
if [[ $create_venv != "n" && $create_venv != "N" ]]; then
    echo "Creating virtual environment..."
    python3 -m venv ai_assistant_env
    source ai_assistant_env/bin/activate
    echo "✅ Virtual environment created and activated"
fi

# Install system dependencies
echo "🔧 Installing system dependencies..."

if command -v apt-get &> /dev/null; then
    # Ubuntu/Debian
    echo "Detected Ubuntu/Debian system"
    sudo apt-get update
    sudo apt-get install -y python3-tk python3-dev build-essential
    echo "✅ System dependencies installed"
elif command -v yum &> /dev/null; then
    # CentOS/RHEL
    echo "Detected CentOS/RHEL system"
    sudo yum install -y python3-tkinter python3-devel gcc
    echo "✅ System dependencies installed"
elif command -v dnf &> /dev/null; then
    # Fedora
    echo "Detected Fedora system"
    sudo dnf install -y python3-tkinter python3-devel gcc
    echo "✅ System dependencies installed"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "Detected macOS system"
    if command -v brew &> /dev/null; then
        brew install python-tk
        echo "✅ System dependencies installed"
    else
        echo "⚠️  Warning: Homebrew not found. Please install python-tk manually"
    fi
else
    echo "⚠️  Warning: Could not detect package manager. Please install python3-tk manually"
fi

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed successfully"
else
    echo "❌ Error: Failed to install Python dependencies"
    exit 1
fi

# Create desktop shortcut (Linux)
if command -v desktop-file-install &> /dev/null; then
    echo "🖥️  Creating desktop shortcut..."
    cat > ~/Desktop/AI-Assistant.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=AI Desktop Assistant
Comment=Intelligent system monitoring and optimization assistant
Exec=$(pwd)/start_assistant.sh
Icon=$(pwd)/icon.png
Terminal=false
Categories=System;Utility;
EOF
    chmod +x ~/Desktop/AI-Assistant.desktop
    echo "✅ Desktop shortcut created"
fi

# Create startup script
echo "🚀 Creating startup script..."
cat > start_assistant.sh << 'EOF'
#!/bin/bash

# AI Desktop Assistant Startup Script

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Activate virtual environment if it exists
if [ -d "$SCRIPT_DIR/ai_assistant_env" ]; then
    source "$SCRIPT_DIR/ai_assistant_env/bin/activate"
fi

# Change to script directory
cd "$SCRIPT_DIR"

# Run the assistant
python3 main.py
EOF

chmod +x start_assistant.sh
echo "✅ Startup script created"

# Create data directories
echo "📁 Creating data directories..."
mkdir -p ml_data
mkdir -p web_cache
mkdir -p logs
echo "✅ Data directories created"

# Test installation
echo "🧪 Testing installation..."
python3 -c "
import sys
try:
    import psutil
    import requests
    import tkinter as tk
    print('✅ All required modules imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ Installation test passed"
else
    echo "❌ Installation test failed"
    exit 1
fi

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "To start the AI Desktop Assistant:"
echo "  ./start_assistant.sh"
echo ""
echo "Or simply run:"
echo "  python3 main.py"
echo ""
echo "The assistant will start with a GUI interface."
echo ""