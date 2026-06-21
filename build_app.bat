@echo off
setlocal enabledelayedexpansion

title AI 3D Model Designer Compiler
echo ====================================================================
echo             AI 3D Model Designer Application Compiler
echo ====================================================================
echo.

:: 1. Verify Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to your PATH.
    echo Please install Python and check the box "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: 2. Verify and install PyInstaller
echo Verifying PyInstaller installation...
python -m pip install pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install PyInstaller. Please check your internet connection.
    echo.
    pause
    exit /b 1
)

:: 3. Run PyInstaller Compilation
echo.
echo [COMPILING] Starting compilation using PyInstaller spec configuration...
echo This will take a couple of minutes to bundle NumPy, PyVista, Trimesh, and the splash screen...
echo.

pyinstaller --clean AI_3D_Builder.spec

if %errorlevel% eq 0 (
    echo.
    echo ====================================================================
    echo [SUCCESS] Compilation completed successfully!
    echo.
    echo Your standalone application is ready at:
    echo   %~dp0dist\AI_3D_Builder.exe
    echo.
    echo The instant bootloader splash screen has been bundled into the app.
    echo ====================================================================
) else (
    echo.
    echo [ERROR] PyInstaller compilation failed.
    echo Please check the output above for compiler errors.
)
echo.
pause
