"""
toolkit.py
==========
Utilidades personales pequenas y autocontenidas.

Actualmente expone solo zstd para comprimir y descomprimir proyectos.
Las tareas de entorno, secretos y bootstrap viven en infra.
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
ZSTD_SCRIPT = REPO_ROOT / "zstd_project.py"


def _print_header(title: str) -> None:
    print()
    print("=" * 58)
    print(f"  {title}")
    print("=" * 58)


def _run(command: list[str], *, cwd: Path | None = None, check: bool = True) -> int:
    printable = " ".join(shlex.quote(part) for part in command)
    print(f"$ {printable}")
    completed = subprocess.run(command, cwd=str(cwd) if cwd else None, check=False)
    if check and completed.returncode != 0:
        raise subprocess.CalledProcessError(completed.returncode, command)
    return completed.returncode


def command_zstd_passthrough(args: list[str]) -> int:
    if not ZSTD_SCRIPT.exists():
        print(f"[ERROR] No se encontro {ZSTD_SCRIPT}")
        return 1
    return _run([sys.executable, str(ZSTD_SCRIPT), *args], check=False)


def menu() -> int:
    while True:
        print()
        print("╔══════════════════════════════════════════════════════╗")
        print("║        TOOLKIT — Utilidades pequenas aisladas       ║")
        print("╠══════════════════════════════════════════════════════╣")
        print("║  1  ▶  zstd (comprimir / descomprimir)              ║")
        print("║  0  ▶  Salir                                        ║")
        print("╚══════════════════════════════════════════════════════╝")

        option = input("\n  Opcion: ").strip()

        if option == "1":
            command_zstd_passthrough([])
        elif option == "0":
            return 0
        else:
            print("  [ERROR] Opcion no valida.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Toolkit de utilidades pequenas y autocontenidas",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("menu", help="Abrir menu interactivo")

    zstd = sub.add_parser("zstd", help="Comprimir / descomprimir con zstd")
    zstd.add_argument("zstd_args", nargs=argparse.REMAINDER)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command or args.command == "menu":
        return menu()

    if args.command == "zstd":
        return command_zstd_passthrough(args.zstd_args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
