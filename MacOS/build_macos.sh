#!/bin/bash

echo "========================================"
echo "  PyCHAT macOS Builder"
echo "========================================"
echo ""

if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "PyInstaller not found. Installing..."
    pip3 install pyinstaller
    echo ""
fi

echo "Cleaning previous builds..."
rm -rf build dist *.spec
echo ""

echo "Building Terminal Version..."
pyinstaller --onefile --console --name PyChatClient --hidden-import=cryptography --hidden-import=dotenv client.py
echo ""

echo "Building GUI Version..."
pyinstaller --onefile --windowed --name PyChatGUI --hidden-import=cryptography --hidden-import=dotenv clientGUI.py
echo ""

if [ -f "dist/PyChatClient" ] && [ -f "dist/PyChatGUI.app/Contents/MacOS/PyChatGUI" ]; then
    echo "========================================"
    echo "  BUILD SUCCESSFUL!"
    echo "========================================"
    echo ""
    echo "Terminal version: dist/PyChatClient"
    echo "GUI version: dist/PyChatGUI.app"
    echo ""
    echo "To run:"
    echo "  ./dist/PyChatClient"
    echo "  open dist/PyChatGUI.app"
    echo ""
else
    echo "========================================"
    echo "  BUILD FAILED!"
    echo "========================================"
    echo "Check the error messages above"
    echo ""
fi