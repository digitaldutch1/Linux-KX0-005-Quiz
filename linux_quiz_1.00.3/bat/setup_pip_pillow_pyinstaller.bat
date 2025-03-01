@echo off
SETLOCAL

:: Check of pip3 is geïnstalleerd
echo Checking if pip3 is installed...
python -m ensurepip --upgrade
python -m pip --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo pip3 is not installed. Installing pip3...
    python -m ensurepip
)

:: Controleer of pyinstaller is geïnstalleerd
echo Checking if PyInstaller is installed...
python -m pip show pyinstaller >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo PyInstaller is not installed. Installing PyInstaller...
    python -m pip install pyinstaller
)

:: Controleer of Pillow is geïnstalleerd
echo Checking if Pillow is installed...
python -m pip show pillow >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Pillow is not installed. Installing Pillow...
    python -m pip install pillow
)

echo All checks complete!
pause