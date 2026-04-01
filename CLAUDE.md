# CLAUDE.md

Guía para trabajar con el proyecto `toolkit`.

## Project Overview

Mini-repositorio de utilidades autocontenidas. Cada utilidad vive en `utils/` y se expone como comando en la CLI via `toolkit.py`. 

El setup del entorno, secretos, bootstrap de máquina y tareas operativas compartidas viven en `infra`.

## Setup & Running

```bash
# Setup automático (crea venv + instala deps + ejecuta)
bash run.sh      # macOS/Linux
run.bat          # Windows

# O directamente
python toolkit.py [comando]
```

## Available Commands

```bash
# ZSTD — Compresión
python toolkit.py zstd compress <ruta> [--level 9]
python toolkit.py zstd decompress <archivo.tar.zst> --output <destino>
python toolkit.py zstd list <archivo.tar.zst> [--verbose]

# Claude Quota Tracker
python toolkit.py claude status
python toolkit.py claude reset [--hours 2.5 | --minutes 90]
python toolkit.py claude history
```

## Architecture

**Modules in `utils/`:**

- `utils/zstd.py` — Compresión de proyectos completos con Zstandard
- `utils/claude_quota.py` — Tracker de cuota de uso (ventana 5h)

**Entry points:**

- `toolkit.py` — CLI unifyer con menú interactivo
- `scripts/bootstrap.py` — Setup multiplataforma (crea venv, instala, ejecuta)
- `run.sh` / `run.bat` — Wrappers simplificados

## Dependencies

- `zstandard` — comprensión zstd

## Environment Variables

| Variable | Purpose |
|---|---|
| `ZSTD_SOURCE_DIR` | Root dir para operaciones masivas zstd (default: `~/Documents/source`) |
