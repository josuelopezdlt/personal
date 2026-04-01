"""
toolkit.py
==========
Utilidades personales pequenas y autocontenidas.

Expone:
  - zstd: Comprimir/descomprimir proyectos
  - claude: Tracker de cuota de uso de Claude AI

El setup del entorno, secretos y bootstrap viven en infra.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
UTILS_DIR = REPO_ROOT / "utils"

# Importar módulos directamente desde utils/
sys.path.insert(0, str(UTILS_DIR))
from zstd import cli as zstd_cli, menu as zstd_menu
from claude_quota import main as claude_quota_main


def command_zstd(args: list[str]) -> int:
    """Ejecuta zstd con argumentos CLI o menú interactivo."""
    if args:
        return zstd_cli(args)
    else:
        return zstd_menu()


def command_claude(args: list[str]) -> int:
    """Ejecuta claude quota tracker."""
    return claude_quota_main(args if args else [])


def menu() -> int:
    """Menú interactivo principal."""
    while True:
        print()
        print("╔═══════════════════════════════════════════════════════╗")
        print("║       TOOLKIT — Utilidades pequenas aisladas         ║")
        print("╠═══════════════════════════════════════════════════════╣")
        print("║  1  ▶  zstd (comprimir / descomprimir)               ║")
        print("║  2  ▶  claude (cuota de uso)                         ║")
        print("║  0  ▶  Salir                                         ║")
        print("╚═══════════════════════════════════════════════════════╝")

        option = input("\n  Opción: ").strip()

        if option == "1":
            command_zstd([])
        elif option == "2":
            command_claude([])
        elif option == "0":
            print("\n  [!] Saliendo...")
            return 0
        else:
            print("  [ERROR] Opción no válida.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Toolkit de utilidades pequenas y autocontenidas",
        prog="toolkit.py",
    )
    sub = parser.add_subparsers(dest="command", help="Comando a ejecutar")

    # Menu
    sub.add_parser("menu", help="Abrir menú interactivo")

    # ZSTD
    zstd = sub.add_parser("zstd", help="Comprimir / descomprimir con zstd")
    zstd.add_argument("zstd_args", nargs=argparse.REMAINDER)

    # Claude
    claude = sub.add_parser("claude", help="Tracker de cuota de uso de Claude")
    claude.add_argument("claude_args", nargs=argparse.REMAINDER)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "menu" or args.command is None:
        return menu()
    elif args.command == "zstd":
        return command_zstd(args.zstd_args)
    elif args.command == "claude":
        return command_claude(args.claude_args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
