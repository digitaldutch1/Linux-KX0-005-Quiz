


@echo off
echo Cleaning previous build and dist folders...
rd /s /q build
rd /s /q dist

echo Running PyInstaller...
pyinstaller --onefile --add-data "linux_questions;linux_questions" --add-data "C:\\Users\\denni\\Desktop\\linux\\linuxbook\\linuxbook.pdf;." --icon "C:\\Users\\denni\\Desktop\\linux\\icon\\linux_icon.ico" linux.py

echo PyInstaller process completed.
pause