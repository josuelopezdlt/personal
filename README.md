# toolkit

Repositorio de utilidades pequenas y autocontenidas (mini-proyectos standalone).

Cada utilidad vive en `utils/` y se expone via CLI en `toolkit.py`. El setup del entorno y tareas operativas viven en `infra`.

## Inicio rápido

```bash
# Mac / Linux
bash run.sh

# Windows
run.bat

# O directamente (con venv activo)
python toolkit.py [comando]
```

## Comandos

```bash
# Compresión con zstd
python toolkit.py zstd compress <ruta> [--level 9]
python toolkit.py zstd decompress <archivo.tar.zst> --output <destino>
python toolkit.py zstd list <archivo.tar.zst> [--verbose]

# Tracker de cuota Claude AI
python toolkit.py claude status     # Mostrar tiempo restante
python toolkit.py claude reset      # Iniciar contador
python toolkit.py claude history    # Ver historial
```

## Estructura

```
toolkit/
├── toolkit.py           # CLI principal
├── requirements.txt     # Dependencias
├── run.sh / run.bat     # Entrypoints simplificados
├── scripts/
│   └── bootstrap.py     # Setup unificado (crea venv + instala deps)
└── utils/
    ├── __init__.py
    ├── zstd.py         # Compresion de proyectos
    └── claude_quota.py # Tracker de cuota Claude
```
