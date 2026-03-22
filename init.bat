@echo off
:: init.bat — Punto de entrada principal (Windows)
:: Activa el entorno virtual e inicia personal_starter.
:: Uso:  init.bat [argumentos para personal_starter.py]

set SCRIPT_DIR=%~dp0
set VENV_PYTHON=%SCRIPT_DIR%.venv\Scripts\python.exe

:: ── Verificar que el entorno esté instalado ──
if not exist "%VENV_PYTHON%" (
    echo.
    echo   [!] Entorno virtual no encontrado.
    echo   Ejecuta primero:  install.bat
    echo.
    pause
    exit /b 1
)

:: ── Lanzar la herramienta ─────────────────────
"%VENV_PYTHON%" "%SCRIPT_DIR%personal_starter.py" %*
