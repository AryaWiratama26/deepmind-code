#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' 

echo -e "${BLUE}deepmind-code (dmc) Installer${NC}"
echo "================================="

if ! command -v python3 &> /dev/null
then
    echo "Python 3 could not be found. Please install Python 3 first."
    exit 1
fi

if ! command -v pip &> /dev/null
then
    echo "pip could not be found. Please install pip first."
    exit 1
fi

echo -e "\n${BLUE}[1/2]${NC} Installing from GitHub repository..."
pip install --user git+https://github.com/AryaWiratama26/deepmind-code.git

echo -e "\n${GREEN}[2/2] Installation Complete!${NC}"
echo "You can now use the 'dmc' command from anywhere in your terminal."
echo -e "Note: Make sure your local bin directory (e.g. \033[1m~/.local/bin\033[0m) is in your PATH."
echo "Try running:"
echo "  dmc --help"
