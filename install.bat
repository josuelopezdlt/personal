@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
set SCRIPT_DIR=%~dp0
echo.
echo ══════════════════════════════════════════════
echo    Instalador — zstd_project  (setup inicial)
echo ══════════════════════════════════════════════
echo.

:: ── 1. Verificar Python ───────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado en el PATH.
    echo.
    echo  Opciones:
    echo    A) Descarga Python desde https://python.org/downloads
    echo       y marca "Add Python to PATH" al instalar.
    echo    B) Si ya lo tienes instalado, agrega su carpeta al PATH manualmente:
    echo       Configuracion del sistema ^> Variables de entorno ^> PATH
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo [OK] %PYVER% encontrado.

:: ── 2. Crear / reutilizar entorno virtual ─────
set VENV_DIR=%~dp0.venv

if not exist "%VENV_DIR%\" (
    echo   Creando entorno virtual en .venv ...
    python -m venv "%VENV_DIR%"
    echo [OK] Entorno virtual creado.
) else (
    echo [OK] Entorno virtual ya existe.
)

:: ── 3. Instalar dependencias en el venv ───────
echo.
echo   Instalando dependencias...
"%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip --quiet
"%VENV_DIR%\Scripts\python.exe" -m pip install -r "%~dp0requirements.txt"

if errorlevel 1 (
    echo.
    echo [ERROR] Fallo al instalar dependencias.
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas en .venv

:: ── 4. Registrar doskey / acceso directo ──────
echo.
echo   Registrando acceso en variables de usuario...
setx PERSONAL_STARTER_DIR "%SCRIPT_DIR%" >nul 2>&1
echo [OK] Variable PERSONAL_STARTER_DIR registrada.

echo.
echo ══════════════════════════════════════════════
echo    Listo. Formas de arrancar:
echo.
echo    init.bat               → menú interactivo
echo    .venv\Scripts\python personal_starter.py
echo    .venv\Scripts\python personal_starter.py zstd --help
echo ══════════════════════════════════════════════
echo.
pause
