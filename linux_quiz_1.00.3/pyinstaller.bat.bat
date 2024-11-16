


@echo off
echo Cleaning previous build and dist folders...
rd /s /q "%~dp0..\build"
rd /s /q "%~dp0..\dist"

echo Running PyInstaller...
pyinstaller --onefile --add-data "%~dp0assets\linux_questions;assets\linux_questions" --add-data "%~dp0assets\linuxbook\linuxbook.pdf;assets\linuxbook" --icon "%~dp0assets\icon\linux_icon2.ico" "%~dp0linux.py"

echo PyInstaller process completed.
pause