# toolkit

Repositorio de utilidades pequenas y autocontenidas.

Su alcance es guardar mini proyectos standalone, como el descompresor con zstd. El setup del entorno, secretos, bootstrap de máquina y tareas operativas viven en `infra`.

## Inicio rápido

```bash
# Mac / Linux
bash run.sh

# Windows
run.bat
```

El script crea el `.venv` si no existe, instala dependencias y abre el menú interactivo.

También puedes invocar directamente (con el venv activo):

```bash
python toolkit.py [comando]
```

## Comandos

```bash
python toolkit.py zstd compress <ruta> [--level 9]          # Comprimir
python toolkit.py zstd decompress <archivo.tar.zst> --output <destino>
python toolkit.py zstd list <archivo.tar.zst> [--verbose]
```

## Estructura

```
toolkit/
├── toolkit.py        # CLI + menu principal para utilidades pequenas
├── zstd_project.py   # Utilidad standalone de compresion zstd
├── run.sh            # Entrypoint Mac/Linux (crea venv + activa + ejecuta)
├── run.bat           # Entrypoint Windows
└── requirements.txt  # zstandard
```

## Variables de entorno

| Variable | Uso |
|---|---|
| `ZSTD_SOURCE_DIR` | Directorio raíz para operaciones masivas de zstd (default: `~/Documents/source`) |
