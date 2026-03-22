# personal — starter toolkit

Este repositorio ahora es un **punto de partida** para nuevos proyectos:

1. Mantiene la herramienta de compresión/descompresión con zstd.
2. Crea entornos virtuales e instala `requirements` de otros proyectos.
3. Ayuda a inicializar SSH.
4. Valida tokens por variables de entorno.
5. Genera/ejecuta túneles SSH para conectar DBCode a bases remotas.

## Estructura

```
personal/
├── personal_starter.py  # Menú + CLI principal (starter toolkit)
├── zstd_project.py      # Utilidad zstd (menú + CLI)
├── install.sh           # Instalación inicial (macOS/Linux)
├── install.bat          # Instalación inicial (Windows)
├── init.sh              # Entrypoint rápido (macOS/Linux)
├── init.bat             # Entrypoint rápido (Windows)
└── requirements.txt     # Dependencias Python del toolkit
```

## Instalación (primera vez)

### macOS / Linux

```bash
bash install.sh
```

El instalador:

1. Verifica Python 3.
2. Crea `.venv` local.
3. Instala dependencias.
4. Registra alias:
	- `personal` -> CLI principal.
	- `zstd` -> acceso rápido a `personal zstd`.

### Windows

```bat
install.bat
```

## Uso diario

### Menú interactivo

```bash
./init.sh            # macOS/Linux
init.bat             # Windows
```

O directo:

```bash
personal
```

### Comandos CLI del starter

```bash
# Validar herramientas base del sistema
personal doctor

# Crear venv e instalar requirements de otro proyecto
personal setup-project ~/code/mi-proyecto

# Misma operación indicando requirements manualmente
personal setup-project ~/code/mi-proyecto -r ~/code/mi-proyecto/requirements.txt

# Instalar llave SSH exclusivamente desde 1Password
personal ssh-init --vault Engineering --item github-ssh

# Validar tokens por variables de entorno
personal token-check --token GITHUB_TOKEN --token DBCODE_TOKEN

# Generar comando de túnel DBCode
personal dbcode-tunnel --user ubuntu --host bastion.miempresa.com --remote-port 5432

# Abrir el túnel en primer plano
personal dbcode-tunnel --user ubuntu --host bastion.miempresa.com --remote-port 5432 --execute
```

Antes de cualquier comando SSH, inicia sesion en 1Password CLI:

```bash
op signin
```

## zstd (compatible)

Sigue disponible sin romper el flujo anterior:

```bash
personal zstd
personal zstd compress <ruta> --level 9
personal zstd decompress <archivo.tar.zst> --output <destino>
personal zstd list <archivo.tar.zst> --verbose
```

## Flujo sugerido para nuevos proyectos

1. Ejecuta `personal doctor` para validar base local.
2. Crea entorno en el proyecto destino con `personal setup-project`.
3. Instala SSH desde 1Password con `personal ssh-init --vault <vault> --item <item>`.
4. Exporta tokens de forma temporal en sesión (nunca hardcode).
5. Usa `personal dbcode-tunnel` para conectar DBCode vía `localhost`.

## Variables de entorno

| Variable | Uso |
|---|---|
| `ZSTD_SOURCE_DIR` | Directorio raíz para operaciones masivas de zstd. |
| `GITHUB_TOKEN` | Token para integraciones con GitHub (si aplica). |
| `DBCODE_TOKEN` | Token para flujos de DBCode (si aplica). |

## Seguridad

1. No guardes tokens en repositorio.
2. No comitees llaves privadas SSH.
3. SSH se obtiene solo desde 1Password (sin generar llaves locales fuera del vault).
4. Cierra túneles SSH cuando termines.
