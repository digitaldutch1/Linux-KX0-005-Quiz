@echo off
setlocal

REM Controleer of Python is geïnstalleerd
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is niet geïnstalleerd. Downloaden...

    REM Download Python installer
    curl -o python-installer.exe https://www.python.org/ftp/python/3.13.0/python-3.13.0.exe

    REM Voer de Python installer uit
    echo Start Python installatie...
    start /wait python-installer.exe

    REM Verwijder de installer na installatie
    del python-installer.exe
) else (
    echo Python is al geïnstalleerd.
)

REM Zorg ervoor dat pip is geïnstalleerd en up-to-date
python -m ensurepip --upgrade

REM Controleer of SumatraPDF is geïnstalleerd als PDF-lezer
set "SUMATRA_READER=C:\Program Files\SumatraPDF\SumatraPDF.exe"
if not exist "%SUMATRA_READER%" (
    echo SumatraPDF is niet geïnstalleerd. Downloaden...

    REM Download SumatraPDF installer
    curl -o sumatrapdf-installer.exe https://www.sumatrapdfreader.org/dl/SumatraPDF-3.3.3-64-install.exe

    REM Voer de SumatraPDF installer uit
    echo Start SumatraPDF installatie...
    start /wait sumatrapdf-installer.exe

    REM Verwijder de installer na installatie
    del sumatrapdf-installer.exe
) else (
    echo SumatraPDF is al geïnstalleerd.
)

REM Einde van het script
echo Setup voltooid.
endlocal
pause