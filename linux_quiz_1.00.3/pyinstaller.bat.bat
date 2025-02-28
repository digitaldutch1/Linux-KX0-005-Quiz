


@echo off

echo Cleaning previous build and dist folders...

rd /s /q "%~dp0build"
rd /s /q "%~dp0dist"

echo Running PyInstaller...

pyinstaller --onefile ^
--add-data "%~dp0assets\\icon\\linux afbeelding 2.png;assets/icon" ^
--add-data "%~dp0assets\\linux_questions;assets/linux_questions" ^
--add-data "%~dp0assets\\linuxbook\\*.pdf;assets/linuxbook" ^
--add-data "%~dp0assets\\linux_questions_images;assets/linux_questions_images" ^
--icon "%~dp0assets\\icon\\linux_icon2.ico" ^
"%~dp0linux.py"

echo PyInstaller process completed.

pause