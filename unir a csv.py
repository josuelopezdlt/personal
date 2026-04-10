import polars as pl
from pathlib import Path

SOURCE_DIR = Path(r"C:\Users\JosueLopezDeLaTorre\Desktop\anthropic\ventas 2025")
OUTPUT_FILE = SOURCE_DIR / "ventas_2025_unificado.csv"


def unir_excels_a_csv(source_dir: Path, output_file: Path) -> None:
    archivos = sorted(source_dir.glob("*.xls*"))
    if not archivos:
        print(f"No se encontraron archivos Excel en: {source_dir}")
        return

    print(f"Encontrados {len(archivos)} archivos:")
    frames = []
    for archivo in archivos:
        print(f"  Leyendo: {archivo.name}")
        df = pl.read_excel(archivo, engine="calamine")
        frames.append(df)

    unificado = pl.concat(frames, how="diagonal_relaxed")
    unificado.write_csv(output_file)
    print(f"\nUnificado: {len(unificado):,} filas → {output_file}")


if __name__ == "__main__":
    unir_excels_a_csv(SOURCE_DIR, OUTPUT_FILE)
