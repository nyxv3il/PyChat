@echo off
echo ========================================
echo   PyCHAT GUI Client Builder
echo ========================================
echo.

python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    echo.
)

echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec
echo.

echo Building PyChatGUI.exe...
echo This may take a minute...
echo.
pyinstaller --onefile --windowed --name PyChatGUI --hidden-import=cryptography --hidden-import=dotenv clientGUI.py

echo.
if exist dist\PyChatGUI.exe (
    echo ========================================
    echo   BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Your GUI executable is ready at:
    echo   dist\PyChatGUI.exe
    echo.
    echo File size: 
    for %%A in (dist\PyChatGUI.exe) do echo   %%~zA bytes
    echo.
    echo To distribute:
    echo   1. Copy dist\PyChatGUI.exe
    echo   2. Include .env file (optional)
    echo   3. Users can select/generate key in GUI
    echo.
) else (
    echo ========================================
    echo   BUILD FAILED!
    echo ========================================
    echo Check the error messages above
    echo.
)

pause