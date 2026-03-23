# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A personal starter toolkit for managing local development environments. It provides CLI utilities for compression/decompression, project setup, SSH key management via 1Password, token validation, and SSH tunnel creation for database connections.

## Setup & Running

```bash
# First-time setup (creates .venv, installs dependencies, registers aliases)
bash install.sh        # macOS/Linux
install.bat            # Windows

# Launch interactive menu
./init.sh              # macOS/Linux
init.bat               # Windows

# Or invoke directly
python personal_starter.py [command]
```

## Available Commands

```bash
personal doctor                                                    # Validate system tools
personal setup-project <path> [-r requirements.txt]               # Create venv & install deps
personal ssh-init --vault <vault> --item <item>                    # Install SSH key from 1Password
personal token-check --token TOKEN1 [--token TOKEN2]               # Validate env tokens
personal dbcode-tunnel --user <user> --host <host> --remote-port <port> [--execute]
personal zstd compress <path> [--level 9] [--output file.tar.zst]
personal zstd decompress <file.tar.zst> --output <destination>
personal zstd list <file.tar.zst> [--verbose]
```

## Architecture

**Two main modules:**

- `personal_starter.py` — Main CLI application. Organizes commands as `command_*` functions, an interactive `menu()`, `build_parser()` for argparse, and `main()` as entry point. Uses `subprocess` for system calls (pip, git, SSH, 1Password CLI).

- `zstd_project.py` — Standalone compression utility. Can be called directly or via `personal zstd`. Configurable root directory via `ZSTD_SOURCE_DIR` env var (default: `~/Documents/source`). Excludes `.git`, `.venv`, `node_modules`, etc. from archives.

**Design patterns:**
- Dual-mode: interactive menu + direct CLI for every command
- 1Password CLI (`op`) required for all credential operations — no local key generation or hardcoded secrets
- Cross-platform via `pathlib.Path` and `os.name` checks

## Dependencies

**Python**: `zstandard` (only pip dependency)

**System tools required** (validated by `personal doctor`):
- Python 3.x
- Git
- OpenSSH client
- 1Password CLI (`op`)
- VS Code CLI (`code`)

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `ZSTD_SOURCE_DIR` | Root directory for bulk zstd operations |
| `OP_CLI_PATH` | Custom path to 1Password CLI executable |
| `GITHUB_TOKEN`, `DBCODE_TOKEN` | Validated by `token-check` command |

## Security Constraints

- All SSH keys must be provisioned through 1Password (no local key generation)
- Tokens are passed via environment variables only — never hardcoded or committed
- `.env` files are gitignored
