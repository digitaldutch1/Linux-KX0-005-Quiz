


@echo off
setlocal

REM Controleer of Foxit Reader is geïnstalleerd
set "FOXIT_READER=C:\Program Files (x86)\Foxit Software\Foxit Reader\FoxitReader.exe"

if not exist "%FOXIT_READER%" (
    echo Foxit Reader is niet geïnstalleerd. Downloaden...

    REM Download de Foxit Reader installer
    curl -o foxitreader-installer.exe "https://cdn01.foxitsoftware.com/product/reader/desktop/win/12.0/FoxitPDFReader120_L10N_Setup_Prom.exe"

    if exist foxitreader-installer.exe (
        REM Voer de Foxit Reader installer uit
        echo Start Foxit Reader installatie...
        start /wait foxitreader-installer.exe /S

        REM Verwijder de installer na installatie
        del foxitreader-installer.exe
    ) else (
        echo Download mislukt. Controleer je internetverbinding of de URL.
    )
) else (
    echo Foxit Reader is al geïnstalleerd.
)

REM Einde van het script
echo Setup voltooid.

endlocal
pause