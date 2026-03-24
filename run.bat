@echo off
setlocal
set SCRIPT_DIR=%~dp0
set VENV=%SCRIPT_DIR%.venv

if not exist "%VENV%" (
    echo Creando entorno virtual...
    python -m venv "%VENV%"
    "%VENV%\Scripts\pip" install -r "%SCRIPT_DIR%requirements.txt" -q
)

call "%VENV%\Scripts\activate.bat"
python "%SCRIPT_DIR%toolkit.py" %*
