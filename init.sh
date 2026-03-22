#!/usr/bin/env bash
# init.sh — Punto de entrada principal (macOS/Linux)
# Activa el entorno virtual e inicia personal_starter.
# Ejecutar:  ./init.sh [argumentos para personal_starter.py]
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"

# ── Verificar que el entorno esté instalado ──
if [[ ! -f "$VENV_PYTHON" ]]; then
    echo ""
    echo "  ⚠️  Entorno virtual no encontrado."
    echo "  Ejecuta primero:  bash install.sh"
    echo ""
    exit 1
fi

# ── Lanzar la herramienta ─────────────────────
exec "$VENV_PYTHON" "$SCRIPT_DIR/personal_starter.py" "$@"
