#!/usr/bin/env python3
"""
scripts/bootstrap.py — Setup unificado para macOS, Linux y Windows.

Crea .venv si no existe, instala dependencias y ejecuta toolkit.py.
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VENV_DIR = REPO_ROOT / ".venv"


def run(cmd: list[str], **kwargs) -> int:
    """Ejecuta comando con error handling."""
    try:
        return subprocess.run(cmd, **kwargs, check=False).returncode
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def main() -> int:
    python_bin = sys.executable
    
    # Detectar si ya estamos en venv
    in_venv = sys.prefix != sys.base_prefix
    
    if not VENV_DIR.exists():
        print("🔨 Creando entorno virtual...")
        if run([python_bin, "-m", "venv", str(VENV_DIR)]) != 0:
            print("❌ No se pudo crear venv")
            return 1
        print("✅ venv creado")
    
    # Ejecutable pip dentro del venv
    if sys.platform == "win32":
        pip = VENV_DIR / "Scripts" / "pip.exe"
        python_venv = VENV_DIR / "Scripts" / "python.exe"
    else:
        pip = VENV_DIR / "bin" / "pip"
        python_venv = VENV_DIR / "bin" / "python"
    
    if not pip.exists():
        print("❌ venv incompleto")
        return 1
    
    # Instalar dependencias
    requirements = REPO_ROOT / "requirements.txt"
    if requirements.exists():
        print("📦 Instalando dependencias...")
        if run([str(pip), "install", "-q", "-r", str(requirements)]) != 0:
            print("⚠️  Advertencia: problemas al instalar algunas dependencias")
    
    # Ejecutar toolkit
    print()
    return run([str(python_venv), str(REPO_ROOT / "toolkit.py")] + sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
