@echo off
:: Batch script to set up and run the Linux Quiz

:: Step 1: Check if Python 3.13 is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Installing Python 3.13...
    start /wait "" "https://www.python.org/ftp/python/3.13.0/python-3.13.0.exe" /quiet InstallAllUsers=1 PrependPath=1
    if %errorlevel% neq 0 (
        echo Failed to download Python installer.
        exit /b
    )
    echo Python installed successfully.
) else (
    echo Python is already installed.
)

:: Step 2: Check if pip is installed (pip is the Python package manager)
python -m ensurepip --upgrade

:: Step 3: Install the required Python packages (PyInstaller, Pillow, PyMuPDF, etc.)
echo Installing required Python packages...
pip install pyinstaller pillow pymupdf

:: Step 4: Check if required files exist
if not exist "linux_questions" (
    echo The 'linux_questions' directory is missing.
    exit /b
)

if not exist "linuxbook.pdf" (
    echo The 'linuxbook.pdf' file is missing. Please ensure it is in the correct location.
    exit /b
)

:: Step 5: Copy the necessary files to the correct location
echo Copying files to the correct directory...
xcopy /E /I /H /Y "linux_questions" "linux_questions" >nul
xcopy /I /H /Y "linuxbook.pdf" "." >nul

:: Step 6: Check if linux.py exists
if not exist "linux.py" (
    echo The script 'linux.py' does not exist. Please ensure it is in the correct location.
    exit /b
)

:: Step 7: Create the EXE again (make sure the quiz works)
echo Creating executable...
pyinstaller --onefile --add-data "linux_questions;linux_questions" --add-data "linuxbook.pdf;." --icon "icon\linux_icon.ico" linux.py

:: Step 8: Check if Adobe Acrobat Reader is installed
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" /f "Adobe Acrobat Reader" >nul 2>&1
if %errorlevel% neq 0 (
    echo Adobe Acrobat Reader is not installed. Installing...
    start /wait "" "C:\Users\denni\Desktop\linux\linux_quiz_1.00.2\pdf reader\Adobe Acrobat.lnk"
) else (
    echo Adobe Acrobat Reader is already installed.
)

:: Step 9: Change directory to the parent folder and start linux.py
echo Starting the quiz...
cd ..
if exist "linux.py" (
    python linux.py
    if %errorlevel% neq 0 (
        echo Failed to start linux.py. Please check for errors above.
        exit /b
    )
) else (
    echo The script 'linux.py' was not found in the parent directory.
    exit /b
)