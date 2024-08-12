@echo off
REM Check if the correct number of arguments is provided
if "%~1"=="" (
    echo Usage: z-- filename
    exit /b 1
)

REM Get the full path of the script
set SCRIPT_DIR=%~dp0

REM Run the Python script with the provided filename
python "%SCRIPT_DIR%z--.py" %1
