# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

Toolkit de utilidades pequenas y autocontenidas. Este repo guarda mini proyectos standalone que no pertenecen a un dominio de negocio. El setup del entorno (venvs, SSH, tokens, túneles) vive en `infra`.

## Setup & Running

```bash
# Mac/Linux — crea .venv si no existe, activa y ejecuta
bash run.sh

# Windows
run.bat

# O directamente con el venv activo
python toolkit.py [comando]
```

## Available Commands

```bash
python toolkit.py zstd compress <path> [--level 9] [--output file.tar.zst]
python toolkit.py zstd decompress <file.tar.zst> --output <destino>
python toolkit.py zstd list <file.tar.zst> [--verbose]
```

## Architecture

**Two modules:**

- `toolkit.py` — CLI principal. Expone utilidades pequeñas y el menú interactivo cuando se invoca sin argumentos.
- `zstd_project.py` — Utilidad de compresión standalone. Invocada vía passthrough desde `toolkit.py zstd` o directamente. Configurable con `ZSTD_SOURCE_DIR`.

## Dependencies

**Python**: `zstandard`

## Environment Variables

| Variable | Purpose |
|---|---|
| `ZSTD_SOURCE_DIR` | Directorio raíz para operaciones masivas de zstd |
