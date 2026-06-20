@echo off
setlocal enabledelayedexpansion

title AI 3D Model Designer Launcher
echo ====================================================================
echo             AI 3D Model Designer Launcher (Plug and Play)
echo ====================================================================
echo.

:: 1. Verify Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to your PATH.
    echo Please install Python 3.10 or newer from https://python.org
    echo Make sure to check the box "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: 2. Create Desktop Shortcut (if it doesn't exist)
set "SHORTCUT_PATH=%USERPROFILE%\Desktop\AI 3D Builder.lnk"
if not exist "%SHORTCUT_PATH%" (
    echo Creating Desktop Shortcut...
    powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_PATH%'); $Shortcut.TargetPath = '%~dp0run_3d_builder.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Description = 'Launch AI 3D Model Designer'; $Shortcut.Save()"
    if !errorlevel! eq 0 (
        echo [SUCCESS] Desktop shortcut 'AI 3D Builder' created successfully.
    ) else (
        echo [WARNING] Could not create Desktop shortcut automatically.
    )
)

:: 3. Install core dependencies
echo Verifying python dependencies...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install numpy scipy trimesh pyvista pyvistaqt PyQt6 pywin32 >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Some dependencies could not be pre-installed. Attempting runtime dynamic import...
)

:: 4. Start the Application
echo Launching 3D Designer...
python 3D_Model_Designer.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application exited with error code %errorlevel%.
    echo Please check 'error_log.txt' in the application folder for details.
    pause
)
