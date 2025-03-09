


@echo off

rem Switch to where this BAT file is located
cd /d "%~dp0"

echo Cleaning old build/dist folders...
rd /s /q "build" 2>nul
rd /s /q "dist" 2>nul

echo Running PyInstaller via python -m PyInstaller...

python -m PyInstaller ^
  --onefile ^
  --name "linux_quiz" ^
  --distpath "." ^
  --workpath "build" ^
  --specpath "." ^
  --add-data "assets\icon\linux afbeelding 2.png;assets/icon" ^
  --add-data "assets\linux_questions;assets/linux_questions" ^
  --add-data "assets\linuxbook\*.pdf;assets/linuxbook" ^
  --add-data "assets\linux_questions_images;assets/linux_questions_images" ^
  --icon "assets\icon\linux_icon2.ico" ^
  linux.py

echo PyInstaller process completed.
pause