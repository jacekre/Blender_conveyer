@echo off
REM Quick test render - only 3 frames

echo Starting quick test render (3 frames only)...
echo.

where blender >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Blender not found in PATH
    pause
    exit /b 1
)

blender --background --python scripts\test_render.py

echo.
echo Test complete! Check renders/test folder.
pause
