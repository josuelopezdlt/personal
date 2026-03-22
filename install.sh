#!/usr/bin/env bash
# install.sh — macOS/Linux
# Configura el entorno completo y registra los alias de arranque en el shell.
set -e

echo ""
echo "══════════════════════════════════════════════"
echo "   Instalador — zstd_project  (setup inicial)"
echo "══════════════════════════════════════════════"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── 1. Verificar Python ───────────────────────
if command -v python3 &>/dev/null; then
    PYTHON=python3
    echo "[OK] $(python3 --version) encontrado."
elif command -v python &>/dev/null; then
    PYTHON=python
    echo "[OK] $(python --version) encontrado."
else
    echo "[ERROR] Python no encontrado."
    echo ""
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  Instala con Homebrew:"
        echo "    brew install python"
        echo ""
        echo "  O descarga desde: https://python.org/downloads"
    else
        echo "  Instala con tu gestor de paquetes:"
        echo "    sudo apt install python3   # Debian/Ubuntu"
        echo "    sudo dnf install python3   # Fedora"
    fi
    echo ""
    exit 1
fi

# ── 2. Crear / reutilizar entorno virtual ─────
VENV_DIR="$SCRIPT_DIR/.venv"

if [[ ! -d "$VENV_DIR" ]]; then
    echo "  Creando entorno virtual en .venv ..."
    $PYTHON -m venv "$VENV_DIR"
    echo "[OK] Entorno virtual creado."
else
    echo "[OK] Entorno virtual ya existe."
fi

# Activar el venv para el resto del script
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"
PYTHON="$VENV_DIR/bin/python"

# ── 3. Instalar dependencias en el venv ───────
echo ""
echo "  Instalando dependencias..."
"$PYTHON" -m pip install --upgrade pip --quiet
"$PYTHON" -m pip install -r "$SCRIPT_DIR/requirements.txt"
echo "[OK] Dependencias instaladas en .venv"

# ── 4. Registrar alias en el shell ────────────
SHELL_RC=""
if [[ "$OSTYPE" == "darwin"* ]]; then
    if [[ "$SHELL" == */zsh ]]; then
        SHELL_RC="$HOME/.zshrc"
    else
        SHELL_RC="$HOME/.bash_profile"
    fi
else
    SHELL_RC="$HOME/.bashrc"
fi

ALIAS_LINE="alias personal='$VENV_DIR/bin/python $SCRIPT_DIR/personal_starter.py'"
ZSTD_ALIAS_LINE="alias zstd='personal zstd'"
if ! grep -qF "$ALIAS_LINE" "$SHELL_RC" 2>/dev/null; then
    {
        echo ""
        echo "# personal starter — setup inicial"
        echo "$ALIAS_LINE"
        echo "$ZSTD_ALIAS_LINE"
    } >> "$SHELL_RC"
    echo "[OK] Alias 'personal' y 'zstd' registrados en $SHELL_RC"
    echo "     Recarga con: source $SHELL_RC"
else
    echo "[OK] Alias 'personal' ya estaba registrado en $SHELL_RC"
fi

# ── 5. Generar init.sh ejecutable ─────────────
INIT_SCRIPT="$SCRIPT_DIR/init.sh"
chmod +x "$INIT_SCRIPT" 2>/dev/null || true

echo ""
echo "══════════════════════════════════════════════"
echo "   Listo. Formas de arrancar:"
echo ""
echo "   ./init.sh              → menú interactivo"
echo "   source $SHELL_RC"
echo "   personal               → alias global"
echo "   zstd                   → acceso rápido a herramientas zstd"
echo "══════════════════════════════════════════════"
echo ""
