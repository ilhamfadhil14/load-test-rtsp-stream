#!/bin/bash

# RTSP Load Tester - Quick Setup Script for Unix/Linux/macOS

set -e

echo "=========================================="
echo "RTSP Load Tester - Quick Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo "Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    echo -e "${GREEN}✓${NC} Python 3 found: $(python3 --version)"
else
    echo -e "${RED}✗${NC} Python 3 not found"
    exit 1
fi

# Check FFmpeg
echo "Checking FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo -e "${GREEN}✓${NC} FFmpeg found: $(ffmpeg -version | head -n1)"
else
    echo -e "${RED}✗${NC} FFmpeg not found"
    echo "Please install FFmpeg first:"
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "  sudo apt-get install ffmpeg"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  brew install ffmpeg"
    fi
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${YELLOW}!${NC} Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python packages
echo "Installing Python packages..."
pip install -r requirements.txt
echo -e "${GREEN}✓${NC} Python packages installed"

# Create directories
echo ""
echo "Creating directories..."
mkdir -p videos logs
echo -e "${GREEN}✓${NC} Directories created"

# Check for MediaMTX
echo ""
echo "Checking for MediaMTX..."
if [ -f "mediamtx" ]; then
    echo -e "${GREEN}✓${NC} MediaMTX found"
else
    echo -e "${YELLOW}!${NC} MediaMTX not found"
    echo "Would you like to download MediaMTX? (yes/no)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "Downloading MediaMTX..."
        
        # Detect OS and architecture
        OS=$(uname -s | tr '[:upper:]' '[:lower:]')
        ARCH=$(uname -m)
        
        if [ "$ARCH" = "x86_64" ]; then
            ARCH="amd64"
        elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
            ARCH="arm64"
        fi
        
        VERSION="v1.5.0"
        FILE="mediamtx_${VERSION}_${OS}_${ARCH}.tar.gz"
        URL="https://github.com/bluenviron/mediamtx/releases/download/${VERSION}/${FILE}"
        
        echo "Downloading from: $URL"
        curl -L -o mediamtx.tar.gz "$URL"
        tar -xzf mediamtx.tar.gz
        rm mediamtx.tar.gz
        chmod +x mediamtx
        echo -e "${GREEN}✓${NC} MediaMTX downloaded"
    fi
fi

# Generate test videos
echo ""
echo "Would you like to generate test videos? (yes/no)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "Generating test videos..."
    $PYTHON_CMD video_generator.py
    echo -e "${GREEN}✓${NC} Test videos generated"
fi

# Final instructions
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Start MediaMTX in a separate terminal:"
echo "       ./mediamtx"
echo ""
echo "  2. Run the load test:"
echo "       python main.py"
echo ""
echo "  3. Or run the consumer example:"
echo "       python consumer_example.py rtsp://localhost:8554/stream1"
echo ""
echo "For more information, see README.md"
echo ""
