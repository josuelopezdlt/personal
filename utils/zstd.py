"""
utils/zstd.py — Compresión de proyectos con Zstandard.
"""

import argparse
import datetime
import os
import tarfile
import sys
import time
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import zstandard as zstd
except ImportError:
    print("❌ Falta 'zstandard'. Instala con: pip install zstandard")
    sys.exit(1)

_source_env = os.environ.get("ZSTD_SOURCE_DIR", "")
SOURCE_DIR = Path(_source_env).expanduser().resolve() if _source_env else Path.home() / "Documents" / "source"

BASE_EXCLUDE = {
    "__pycache__", ".git", ".venv", "venv", "env", "node_modules",
    ".mypy_cache", ".pytest_cache", "dist", "build", "*.egg-info",
    ".DS_Store", "Thumbs.db", "personal",
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


def default_output_name(source: Path) -> str:
    date = datetime.date.today().strftime("%Y%m%d")
    return str(source / f"Source_Completo_{date}.tar.zst")


def resolve_output(source: Path, output_arg: str) -> str:
    if output_arg:
        return output_arg if output_arg.endswith(".tar.zst") else output_arg + ".tar.zst"
    return default_output_name(source)


def find_zst_files(search_dir: Path) -> list[Path]:
    found = sorted(search_dir.glob("*.tar.zst")) + sorted(search_dir.parent.glob("*.tar.zst"))
    seen = set()
    result = []
    for p in found:
        if p not in seen:
            seen.add(p)
            result.append(p)
    return result


def compress(source_dir: str, output_file: str = "", level: int = 9, threads: int = 0):
    source = Path(source_dir).resolve()
    if not source.exists():
        print(f"❌ No existe: {source}")
        return

    output = resolve_output(source, output_file)
    print()
    print(f"  📦 Proyecto:  {source.name}")
    print(f"  📁 Destino:   {output}")
    print(f"  ⚡ Nivel:     {level}  |  Threads: auto")
    print(f"  ℹ️  Excluye:  .git  .venv  __pycache__  node_modules")
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


def decompress(input_file: str, output_dir: str):
    input_path = Path(input_file).resolve()
    if not input_path.exists():
        print(f"\n  ❌ No existe: {input_path}")
        return
    if not input_path.is_file():
        print(f"\n  ❌ No es un archivo: {input_path}")
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


def list_contents(input_file: str, verbose: bool = False):
    input_path = Path(input_file).resolve()
    if not input_path.exists():
        print(f"\n  ❌ No existe: {input_path}")
        return
    if not input_path.is_file():
        print(f"\n  ❌ No es un archivo: {input_path}")
        return

    print()
    print(f"  📋 Contenido de: {input_path.name}")
    print("  " + "─" * 53)

    dctx = zstd.ZstdDecompressor()
    total_files = 0
    total_bytes = 0
    top_folders: dict[str, int] = {}  # folder -> file count

    with open(input_path, "rb") as f_in:
        with dctx.stream_reader(f_in) as decompressor:
            with tarfile.open(fileobj=decompressor, mode="r|") as tar:
                for member in tar:
                    if member.isfile():
                        total_files += 1
                        total_bytes += member.size
                        parts = Path(member.name).parts
                        folder = parts[1] if len(parts) > 1 else "(raíz)"
                        top_folders[folder] = top_folders.get(folder, 0) + 1

    print()
    for folder, count in sorted(top_folders.items()):
        print(f"  📁  {folder:<30} {count:>5} archivos")

    print()
    print(f"     Carpetas:    {len(top_folders)}")
    print(f"     Archivos:    {total_files}")
    print(f"     Tamaño orig: {human_size(total_bytes)}")
    print(f"     Comprimido:  {human_size(input_path.stat().st_size)}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Comprime/descomprime proyectos con Zstandard")
    subparsers = parser.add_subparsers(dest="command", required=True)

    c = subparsers.add_parser("compress", help="Comprimir un directorio")
    c.add_argument("source", help="Ruta del proyecto a comprimir")
    c.add_argument("--output", default="", help="Archivo de salida (.tar.zst)")
    c.add_argument("--level", type=int, default=9, choices=range(1, 23), help="Nivel de compresión 1-22")

    d = subparsers.add_parser("decompress", help="Descomprimir un archivo .tar.zst")
    d.add_argument("input", help="Archivo .tar.zst a descomprimir")
    d.add_argument("--output", default=".", help="Directorio de destino")

    ls = subparsers.add_parser("list", help="Listar contenido sin extraer")
    ls.add_argument("input", help="Archivo .tar.zst a inspeccionar")
    ls.add_argument("--verbose", "-v", action="store_true", help="Mostrar cada archivo")

    return parser


def cli(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "compress":
        compress(args.source, args.output, level=args.level)
    elif args.command == "decompress":
        decompress(args.input, args.output)
    elif args.command == "list":
        list_contents(args.input, verbose=args.verbose)
    return 0


def _pick_zst_from_source() -> str | None:
    files = sorted(SOURCE_DIR.glob("*.tar.zst"))
    if not files:
        print(f"\n  ❌ No hay archivos .tar.zst en {SOURCE_DIR}")
        return None
    print()
    for i, f in enumerate(files, 1):
        size = human_size(f.stat().st_size)
        print(f"  {i}  {f.name}  ({size})")
    print()
    raw = input("  Selecciona un archivo: ").strip()
    try:
        idx = int(raw) - 1
        if 0 <= idx < len(files):
            return str(files[idx])
    except ValueError:
        pass
    print("  [ERROR] Selección inválida.")
    return None


def menu() -> int:
    while True:
        print()
        print("╔══════════════════════════════════════════════╗")
        print("║            ZSTD — UTILIDAD CLI              ║")
        print("╠══════════════════════════════════════════════╣")
        print("║  1  ▶  Comprimir                            ║")
        print("║  2  ▶  Descomprimir                         ║")
        print("║  3  ▶  Listar contenido                     ║")
        print("║  0  ▶  Volver                               ║")
        print("╚══════════════════════════════════════════════╝")

        option = input("\n  Opción: ").strip()

        if option == "1":
            output = default_output_name(SOURCE_DIR)
            level_raw = input("  Nivel [1-22] (default 9): ").strip()
            level = 9
            if level_raw:
                try:
                    level = int(level_raw)
                except ValueError:
                    print("  [ERROR] Nivel inválido, usando 9.")
                    level = 9
            cli(["compress", str(SOURCE_DIR), "--level", str(level), "--output", output])
        elif option == "2":
            input_file = _pick_zst_from_source()
            if input_file:
                cli(["decompress", input_file, "--output", str(SOURCE_DIR)])
        elif option == "3":
            input_file = _pick_zst_from_source()
            if input_file:
                cli(["list", input_file])
        elif option == "0":
            return 0
        else:
            print("  [ERROR] Opción no válida.")


if __name__ == "__main__":
    raise SystemExit(cli())
