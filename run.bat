@echo off
REM Batch script to run Blender conveyor simulation
REM Make sure Blender is in your PATH or modify the blender command below

echo Starting Blender Conveyor Simulation...
echo.

REM Check if blender is in PATH
where blender >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Blender not found in PATH
    echo Please install Blender or add it to your PATH
    echo Example: set PATH=%%PATH%%;C:\Program Files\Blender Foundation\Blender 5.0
    pause
    exit /b 1
)

REM Run the simulation
blender --background --python scripts\main.py

echo.
echo Simulation complete! Check the renders folder.
pause
