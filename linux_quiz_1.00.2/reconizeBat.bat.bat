


@echo off

:: Stap 1: Herstel de .bat bestandstype associatie naar de standaard instellingen
echo Herstellen van .bat bestandstype associatie...
assoc .bat=batfile

:: Stap 2: Herstel de ftype voor .bat bestanden naar de standaard instelling
echo Herstellen van .bat file uitvoer...
ftype batfile="%SystemRoot%\System32\cmd.exe" /c "%1" %*

:: Stap 3: Controleer of de instellingen correct zijn
echo Controleer de associatie voor .bat bestandstype:
assoc .bat
echo Controleer de uitvoerinstellingen voor .bat bestanden:
ftype batfile

echo .bat bestandstype is nu hersteld. Probeer het batchbestand opnieuw uit te voeren.

pause