# Building PyCHAT for macOS

## Prerequisites

Make sure you have Python 3 installed:

```bash
python3 --version
```

If not installed, get it from [python.org](https://www.python.org/downloads/macos/) or use Homebrew:

```bash
brew install python3
```

## Step 1: Install Dependencies

```bash
pip3 install -r requirements.txt
pip3 install pyinstaller
```

## Step 2: Build the Apps

### Option A: Using the Build Script (Recommended)

Make the script executable:

```bash
chmod +x build_macos.sh
```

Run it:

```bash
./build_macos.sh
```

### Option B: Manual Build

**Terminal Version:**

```bash
pyinstaller --onefile --console --name PyChatClient \
    --hidden-import=cryptography --hidden-import=dotenv \
    client_encrypted.py
```

**GUI Version:**

```bash
pyinstaller --onefile --windowed --name PyChatGUI \
    --hidden-import=cryptography --hidden-import=dotenv \
    client_gui.py
```

## Step 3: Find Your Apps

After building:

```
dist/
├── PyChatClient          (Terminal app - Unix executable)
└── PyChatGUI.app         (GUI app - macOS application bundle)
```

## Running the Apps

**Terminal Version:**

```bash
./dist/PyChatClient
```

**GUI Version:**

```bash
open dist/PyChatGUI.app
```

Or double-click `PyChatGUI.app` in Finder.

## Distribution

### For Terminal Version

Just distribute the `PyChatClient` file. Users can run it with:

```bash
./PyChatClient
```

### For GUI Version

Distribute the entire `PyChatGUI.app` bundle. Users can:

- Double-click to open
- Drag to Applications folder
- Right-click → Open (first time, to bypass Gatekeeper)

## Code Signing (Optional but Recommended)

To avoid "unidentified developer" warnings:

```bash
codesign --force --deep --sign - dist/PyChatGUI.app
```

For distribution, use a valid Apple Developer certificate:

```bash
codesign --force --deep --sign "Developer ID Application: Your Name" dist/PyChatGUI.app
```

## Creating a DMG Installer

Install `create-dmg`:

```bash
brew install create-dmg
```

Create installer:

```bash
create-dmg \
  --volname "PyChatGUI Installer" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "PyChatGUI.app" 200 190 \
  --hide-extension "PyChatGUI.app" \
  --app-drop-link 600 185 \
  "PyChatGUI-Installer.dmg" \
  "dist/PyChatGUI.app"
```

## Troubleshooting

### "PyChatGUI.app is damaged and can't be opened"

Remove quarantine attribute:

```bash
xattr -cr dist/PyChatGUI.app
```

### "command not found: pyinstaller"

Make sure pip bin is in PATH:

```bash
export PATH="$HOME/Library/Python/3.x/bin:$PATH"
```

Or use:

```bash
python3 -m PyInstaller ...
```

### Tkinter not found

Install Python with Tkinter support:

```bash
brew install python-tk@3.11
```

### App won't start (GUI version)

Check console for errors:

```bash
./dist/PyChatGUI.app/Contents/MacOS/PyChatGUI
```

## Universal Binary (Intel + Apple Silicon)

To create an app that runs on both Intel and Apple Silicon Macs, you need to:

1. Build on an Apple Silicon Mac with:

```bash
pyinstaller --onefile --windowed --target-arch universal2 --name PyChatGUI client_gui.py
```

Or build separately on each architecture and use `lipo` to combine.

## File Size

Expect:

- Terminal version: ~20-30 MB
- GUI version: ~25-35 MB

These include the entire Python interpreter and all dependencies.

## Testing

Always test on a clean Mac without Python installed to ensure everything works standalone.

## Cross-Platform Building

**Important:** PyInstaller creates platform-specific executables. You **cannot** build a macOS app on Windows or vice versa.

To distribute for multiple platforms:

- Build on macOS for macOS
- Build on Windows for Windows
- Build on Linux for Linux

Or use a CI/CD service like GitHub Actions to build for all platforms automatically.

## Next Steps

- Add custom icon with `--icon=icon.icns`
- Create Info.plist for app metadata
- Notarize for macOS Catalina+ (requires Apple Developer account)
- Set up automatic updates

---

**Your app is now ready for macOS! 🍎**

_This Build Script And Instructions File Was Written With The Help Of AI_
