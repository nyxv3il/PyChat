#!/bin/sh

echo "Checking operating system..."
OS="$(uname)"

if [ "$OS" = "Linux" ]; then
    echo "Linux detected."
elif [ "$OS" = "Darwin" ]; then
    echo "macOS detected."
else
    echo "Unsupported OS: $OS"
    exit 1
fi

echo ""
echo "Enter installation directory (full path):"
read INSTALL_DIR

if [ ! -d "$INSTALL_DIR" ]; then
    echo "Directory does not exist. Creating it..."
    mkdir -p "$INSTALL_DIR" || {
        echo "Failed to create directory."
        exit 1
    }
fi

echo "Copying application files..."
cp -r client.py clientGUI.py encryption.py requirements.txt "$INSTALL_DIR"
cp -r .env LICENSE README.md "$INSTALL_DIR" 2>/dev/null

echo "Creating virtual environment..."
cd "$INSTALL_DIR" || exit 1
python3 -m venv venv || {
    echo "Failed to create virtual environment."
    exit 1
}

echo "Installing dependencies..."
"$INSTALL_DIR/venv/bin/pip" install -r requirements.txt

echo "Creating run script..."
cat << 'EOF' > "$INSTALL_DIR/run_app.sh"
#!/bin/sh
DIR="$(cd "$(dirname "$0")" && pwd)"
. "$DIR/venv/bin/activate"
python3 "$DIR/clientGUI.py"
EOF

chmod +x "$INSTALL_DIR/run_app.sh"

echo ""
echo "Installation complete."
echo "Launch the app with:"
echo "sh \"$INSTALL_DIR/run_app.sh\""
