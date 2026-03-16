"""
zstd_project.py
================
Comprime y descomprime proyectos con Zstandard (zstd).

Uso interactivo (menú):
    python zstd_project.py

Uso directo (CLI):
    python zstd_project.py compress <ruta> [--output archivo.tar.zst] [--level 9]
    python zstd_project.py decompress <archivo.tar.zst> [--output ruta_destino]
    python zstd_project.py list <archivo.tar.zst> [--verbose]

Instalación:
    pip install zstandard
"""

import argparse
import tarfile
import sys
import time
from pathlib import Path

# Forzar UTF-8 en Windows para soportar emojis en la terminal
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import zstandard as zstd
except ImportError:
    print("❌ Falta 'zstandard'. Instala con: pip install zstandard")
    sys.exit(1)


# ─────────────────────────────────────────────
# Patrones a EXCLUIR siempre
# ─────────────────────────────────────────────
SOURCE_DIR = Path.home() / "Source"

BASE_EXCLUDE = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    "dist",
    "build",
    "*.egg-info",
    ".DS_Store",
    "Thumbs.db",
}


def should_exclude(path: str, patterns: set[str]) -> bool:
    for part in Path(path).parts:
        if part in patterns:
            return True
        for pattern in patterns:
            if "*" in pattern and Path(part).match(pattern):
                return True
    return False


def human_size(num_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} TB"


def resolve_output(source: Path, output_arg: str) -> str:
    if output_arg:
        return output_arg if output_arg.endswith(".tar.zst") else output_arg + ".tar.zst"
    return str(source.parent / f"{source.name}.tar.zst")


def find_zst_files(search_dir: Path) -> list[Path]:
    """Busca archivos .tar.zst en el directorio dado y en el padre."""
    found = sorted(search_dir.glob("*.tar.zst")) + sorted(search_dir.parent.glob("*.tar.zst"))
    # deduplicar manteniendo orden
    seen = set()
    result = []
    for p in found:
        if p not in seen:
            seen.add(p)
            result.append(p)
    return result


# ─────────────────────────────────────────────
# COMPRIMIR
# ─────────────────────────────────────────────
def compress(source_dir: str, output_file: str = "", level: int = 9, threads: int = 0):
    """Comprime el directorio completo (incluye data/, logs/, reports/)."""
    source = Path(source_dir).resolve()
    if not source.exists():
        print(f"❌ No existe: {source}")
        return

    output = resolve_output(source, output_file)

    print()
    print(f"  📦 Proyecto:  {source.name}")
    print(f"  📁 Destino:   {output}")
    print(f"  ⚡ Nivel:     {level}  |  Threads: auto")
    print(f"  ℹ️  Excluye:  .git  .venv  __pycache__  node_modules  (TODO lo demás incluido: .env, DBs, tokens)")
    print("  " + "─" * 53)

    start = time.time()
    file_count = 0
    original_bytes = 0

    cctx = zstd.ZstdCompressor(level=level, threads=threads if threads > 0 else -1)

    with open(output, "wb") as f_out:
        with cctx.stream_writer(f_out, closefd=False) as compressor:
            with tarfile.open(fileobj=compressor, mode="w|") as tar:
                for item in sorted(source.rglob("*")):
                    rel = str(item.relative_to(source.parent))
                    if should_exclude(rel, BASE_EXCLUDE):
                        continue
                    try:
                        tar.add(item, arcname=rel, recursive=False)
                    except PermissionError:
                        print(f"\n  ⚠️  Omitido (en uso): {rel}")
                        continue
                    if item.is_file():
                        original_bytes += item.stat().st_size
                        file_count += 1
                        if file_count % 50 == 0:
                            print(f"  → {file_count} archivos procesados...", end="\r")

    elapsed = time.time() - start
    compressed_size = Path(output).stat().st_size
    ratio = (1 - compressed_size / original_bytes) * 100 if original_bytes > 0 else 0

    print(f"  → {file_count} archivos procesados.   ")
    print()
    print(f"  ✅ Completado en {elapsed:.1f}s")
    print(f"     Archivos:   {file_count}")
    print(f"     Original:   {human_size(original_bytes)}")
    print(f"     Comprimido: {human_size(compressed_size)}")
    print(f"     Ratio:      {ratio:.1f}% reducción")
    print(f"     Guardado:   {output}")


# ─────────────────────────────────────────────
# DESCOMPRIMIR
# ─────────────────────────────────────────────
def decompress(input_file: str, output_dir: str):
    input_path = Path(input_file).resolve()
    if not input_path.exists():
        print(f"\n  ❌ No existe: {input_path}")
        return

    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    print()
    print(f"  📂 Archivo:  {input_path.name}")
    print(f"  📁 Destino:  {output}")
    print("  " + "─" * 53)

    start = time.time()
    file_count = 0

    dctx = zstd.ZstdDecompressor()

    with open(input_path, "rb") as f_in:
        with dctx.stream_reader(f_in) as decompressor:
            with tarfile.open(fileobj=decompressor, mode="r|") as tar:
                for member in tar:
                    tar.extract(member, path=output, filter="data")
                    if member.isfile():
                        file_count += 1
                        if file_count % 50 == 0:
                            print(f"  → {file_count} archivos extraídos...", end="\r")

    elapsed = time.time() - start
    print(f"  → {file_count} archivos extraídos.   ")
    print()
    print(f"  ✅ Completado en {elapsed:.1f}s")
    print(f"     Archivos:  {file_count}")
    print(f"     Ubicación: {output}")


# ─────────────────────────────────────────────
# LISTAR CONTENIDO
# ─────────────────────────────────────────────
def list_contents(input_file: str, verbose: bool = False):
    input_path = Path(input_file).resolve()
    if not input_path.exists():
        print(f"\n  ❌ No existe: {input_path}")
        return

    print()
    print(f"  📋 Contenido de: {input_path.name}")
    print("  " + "─" * 53)

    dctx = zstd.ZstdDecompressor()
    total_files = 0
    total_dirs = 0
    total_bytes = 0

    with open(input_path, "rb") as f_in:
        with dctx.stream_reader(f_in) as decompressor:
            with tarfile.open(fileobj=decompressor, mode="r|") as tar:
                for member in tar:
                    if member.isfile():
                        total_files += 1
                        total_bytes += member.size
                        if verbose:
                            print(f"  {human_size(member.size):>10}  {member.name}")
                    elif member.isdir():
                        total_dirs += 1

    print(f"\n     Directorios: {total_dirs}")
    print(f"     Archivos:    {total_files}")
    print(f"     Tamaño orig: {human_size(total_bytes)}")
    print(f"     Comprimido:  {human_size(input_path.stat().st_size)}")


# ─────────────────────────────────────────────
# MENÚ INTERACTIVO
# ─────────────────────────────────────────────
def menu():
    here = Path.cwd()

    while True:
        print()
        print("╔══════════════════════════════════════════════════════╗")
        print("║          🗜️  ZODIPLAST  —  Backup de Proyecto         ║")
        print("╠══════════════════════════════════════════════════════╣")
        print(f"║  Proyecto actual: {here.name:<35}║")
        print("╠══════════════════════════════════════════════════════╣")
        print("║  1  ▶  Comprimir proyecto actual (nivel 9)           ║")
        print("║  2  ▶  Comprimir todos los proyectos → ~/Source      ║")
        print("║  3  ▶  Comprimir carpeta /source COMPLETA            ║")
        print("║  4  ▶  Descomprimir archivo .tar.zst                 ║")
        print("║  5  ▶  Ver contenido de archivo .tar.zst             ║")
        print("║  0  ▶  Salir                                         ║")
        print("╚══════════════════════════════════════════════════════╝")

        opcion = input("\n  Opción: ").strip()

        # ── COMPRIMIR ──────────────────────────────────────────
        if opcion == "1":
            print(f"\n  Comprimirá: {here}")
            destino_default = here.parent / f"{here.name}.tar.zst"
            entrada = input(f"  Destino [{destino_default}]: ").strip()
            output = entrada if entrada else str(destino_default)
            compress(str(here), output, level=9)
            print()
            input("  Presiona Enter para continuar...")

        # ── COMPRIMIR TODOS LOS PROYECTOS ────────────────────
        elif opcion == "2":
            proyectos = sorted([
                p for p in SOURCE_DIR.iterdir()
                if p.is_dir() and not p.name.startswith(".")
            ])
            if not proyectos:
                print(f"\n  ❌ No se encontraron proyectos en {SOURCE_DIR}")
            else:
                print(f"\n  Comprimirá {len(proyectos)} proyectos → {SOURCE_DIR}")
                print(f"  " + "─" * 53)
                for proyecto in proyectos:
                    output = str(SOURCE_DIR / f"{proyecto.name}.tar.zst")
                    compress(str(proyecto), output, level=9)
            print()
            input("  Presiona Enter para continuar...")

        # ── COMPRIMIR /source COMPLETA ────────────────────────
        elif opcion == "3":
            output = str(SOURCE_DIR / "Source.tar.zst")
            print(f"\n  Comprimirá TODA la carpeta: {SOURCE_DIR}")
            print(f"  Destino: {output}")
            compress(str(SOURCE_DIR), output, level=9)
            print()
            input("  Presiona Enter para continuar...")

        # ── DESCOMPRIMIR ───────────────────────────────────────
        elif opcion == "4":
            archivos = find_zst_files(here)

            if archivos:
                print("\n  Archivos .tar.zst encontrados:")
                for i, f in enumerate(archivos, 1):
                    size = human_size(f.stat().st_size)
                    print(f"    {i})  {f.name}  ({size})")
                print(f"    {len(archivos)+1})  Ingresar ruta manualmente")
                sel = input("\n  Selecciona: ").strip()
                try:
                    idx = int(sel) - 1
                    if 0 <= idx < len(archivos):
                        input_file = str(archivos[idx])
                    else:
                        input_file = input("  Ruta del .tar.zst: ").strip()
                except ValueError:
                    input_file = input("  Ruta del .tar.zst: ").strip()
            else:
                input_file = input("\n  Ruta del archivo .tar.zst: ").strip()

            if not input_file:
                print("  ❌ No ingresaste un archivo.")
            else:
                destino_default = here
                entrada = input(f"  Extraer en [{destino_default}]: ").strip()
                output_dir = entrada if entrada else str(destino_default)
                decompress(input_file, output_dir)
            print()
            input("  Presiona Enter para continuar...")

        # ── LISTAR ────────────────────────────────────────────
        elif opcion == "5":
            archivos = find_zst_files(here)

            if archivos:
                print("\n  Archivos .tar.zst encontrados:")
                for i, f in enumerate(archivos, 1):
                    size = human_size(f.stat().st_size)
                    print(f"    {i})  {f.name}  ({size})")
                print(f"    {len(archivos)+1})  Ingresar ruta manualmente")
                sel = input("\n  Selecciona: ").strip()
                try:
                    idx = int(sel) - 1
                    if 0 <= idx < len(archivos):
                        input_file = str(archivos[idx])
                    else:
                        input_file = input("  Ruta del .tar.zst: ").strip()
                except ValueError:
                    input_file = input("  Ruta del .tar.zst: ").strip()
            else:
                input_file = input("\n  Ruta del archivo .tar.zst: ").strip()

            if not input_file:
                print("  ❌ No ingresaste un archivo.")
            else:
                verbose = input("  ¿Mostrar cada archivo? (s/N): ").strip().lower() == "s"
                list_contents(input_file, verbose=verbose)
            print()
            input("  Presiona Enter para continuar...")

        # ── SALIR ─────────────────────────────────────────────
        elif opcion == "0":
            print("\n  👋 Hasta luego.\n")
            break

        else:
            print("\n  ⚠️  Opción no válida.")


# ─────────────────────────────────────────────
# CLI (uso directo sin menú)
# ─────────────────────────────────────────────
def cli():
    parser = argparse.ArgumentParser(
        description="Comprime/descomprime proyectos con Zstandard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python zstd_project.py compress .
  python zstd_project.py compress . --output backup.tar.zst --level 9
  python zstd_project.py decompress backup.tar.zst --output ./restaurado
  python zstd_project.py list backup.tar.zst --verbose
        """,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    c = subparsers.add_parser("compress", help="Comprimir un directorio (completo)")
    c.add_argument("source", help="Ruta del proyecto a comprimir")
    c.add_argument("--output", default="", help="Archivo de salida (.tar.zst)")
    c.add_argument("--level", type=int, default=9, choices=range(1, 23),
                   help="Nivel de compresión 1-22 (default: 9)")
    c.add_argument("--threads", type=int, default=0, help="Threads (0 = auto)")

    d = subparsers.add_parser("decompress", help="Descomprimir un archivo .tar.zst")
    d.add_argument("input", help="Archivo .tar.zst a descomprimir")
    d.add_argument("--output", default=".", help="Directorio de destino")

    ls = subparsers.add_parser("list", help="Listar contenido sin extraer")
    ls.add_argument("input", help="Archivo .tar.zst a inspeccionar")
    ls.add_argument("--verbose", "-v", action="store_true", help="Mostrar cada archivo")

    args = parser.parse_args()

    if args.command == "compress":
        compress(args.source, args.output, level=args.level, threads=args.threads)
    elif args.command == "decompress":
        decompress(args.input, args.output)
    elif args.command == "list":
        list_contents(args.input, verbose=args.verbose)


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Sin argumentos → menú interactivo
        menu()
    else:
        # Con argumentos → CLI directo
        cli()
