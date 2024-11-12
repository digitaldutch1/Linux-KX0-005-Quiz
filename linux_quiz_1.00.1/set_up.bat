


@echo off
:: Batch script to set up and run the Linux Quiz

:: Step 1: Check if Python 3.13 is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Installing Python 3.13...
    start /wait https://www.python.org/ftp/python/3.13.0/python-3.13.0.exe /quiet InstallAllUsers=1 PrependPath=1
) else (
    echo Python is already installed.
)

:: Step 2: Check if pip is installed (pip is the Python package manager)
python -m ensurepip --upgrade

:: Step 3: Install the required Python packages (PyInstaller, Pillow, PyMuPDF, etc.)
echo Installing required Python packages...
pip install pyinstaller pillow pymupdf

:: Step 4: Copy the necessary files to the correct location
echo Copying files to the correct directory...
xcopy /E /I /H /Y "linux_questions" "linux_questions"
xcopy /E /I /H /Y "linuxbook.pdf" "."

:: Step 5: Create the EXE again (make sure the quiz works)
echo Creating executable...
pyinstaller --onefile --add-data "linux_questions;linux_questions" --add-data "linuxbook.pdf;." --icon "linux_icon.ico" linux.py

:: Step 6: Install the PDF reader
echo Installing PDF Reader...
start /wait "Installing PDF Reader" "pdf reader\Reader_nl_install.exe"

:: Step 7: Check if Adobe Acrobat Reader is installed
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" /f "Adobe Acrobat Reader" >nul 2>&1
if %errorlevel% neq 0 (
    echo Adobe Acrobat Reader is not installed. Installing...
    start /wait https://get.adobe.com/reader/download/acrobat/readstep2.html /quiet
) else (
    echo Adobe Acrobat Reader is already installed.
)

:: Step 8: Start the quiz
echo Starting the quiz...
start dist\linux.exe