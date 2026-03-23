"""
personal_starter.py
===================
Starter toolkit para preparar proyectos locales:
- Ejecutar utilidades zstd existentes
- Preparar entorno virtual e instalar requirements de otros proyectos
- Asistencia SSH (llaves y conexión)
- Verificación de tokens via variables de entorno
- Construcción/ejecución de túneles SSH para DBCode
"""

from __future__ import annotations

import argparse
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
ZSTD_SCRIPT = REPO_ROOT / "zstd_project.py"
DEFAULT_REQUIREMENTS_NAMES = ("requirements.txt", "requirements-dev.txt")


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


def _resolve_op_executable() -> str | None:
    env_path = os.environ.get("OP_CLI_PATH", "").strip()
    if env_path and Path(env_path).exists():
        return env_path

    from_path = shutil.which("op")
    if from_path:
        return from_path

    winget_root = Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Packages"
    if winget_root.exists():
        matches = sorted(winget_root.glob("AgileBits.1Password.CLI_*"))
        for match in matches:
            candidate = match / "op.exe"
            if candidate.exists():
                return str(candidate)

    return None


def _has_active_1password_session() -> bool:
    op_executable = _resolve_op_executable()
    if not op_executable:
        return False
    completed = subprocess.run([op_executable, "whoami"], capture_output=True, text=True, check=False)
    return completed.returncode == 0


def _require_1password_session() -> bool:
    op_executable = _resolve_op_executable()
    if not op_executable:
        print("[ERROR] op (1Password CLI) no esta disponible.")
        print("Instala 1Password CLI o define OP_CLI_PATH, luego autentica con: op signin")
        return False
    if not _has_active_1password_session():
        print("[ERROR] No hay sesion activa de 1Password.")
        print("Autentica primero con: op signin")
        return False
    return True


def _python_in_venv(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _default_venv_dir(project_dir: Path) -> Path:
    return project_dir / ".venv"


def _detect_requirements(project_dir: Path) -> list[Path]:
    found: list[Path] = []
    for name in DEFAULT_REQUIREMENTS_NAMES:
        candidate = project_dir / name
        if candidate.exists():
            found.append(candidate)
    return found


def command_doctor() -> int:
    _print_header("Doctor del entorno")

    op_installed = bool(_resolve_op_executable())
    op_session = _has_active_1password_session()

    checks: list[tuple[str, bool, str]] = []
    checks.append(("Python", bool(shutil.which("python") or shutil.which("python3")), "Instalar Python 3"))
    checks.append(("Git", bool(shutil.which("git")), "Instalar Git"))
    checks.append(("SSH", bool(shutil.which("ssh")), "Instalar OpenSSH Client"))
    checks.append(("op (1Password CLI)", op_installed, "Instalar 1Password CLI"))
    checks.append(("op signin (activo)", op_session, "Ejecutar 'op signin'"))
    checks.append(("code (VS Code CLI)", bool(shutil.which("code")), "Activar comando 'code' en PATH"))

    has_error = False
    for name, ok, hint in checks:
        status = "OK" if ok else "FALTA"
        print(f"- {name:<20} {status}")
        if not ok:
            has_error = True
            print(f"  -> Sugerencia: {hint}")

    if has_error:
        print("\nHay dependencias faltantes. Corrigelas antes de automatizar setup.")
        return 1

    print("\nEntorno base listo.")
    return 0


def command_setup_project(project: str, venv: str | None, requirements: list[str], with_pip_upgrade: bool) -> int:
    project_dir = Path(project).expanduser().resolve()
    if not project_dir.exists() or not project_dir.is_dir():
        print(f"[ERROR] Proyecto invalido: {project_dir}")
        return 1

    venv_dir = Path(venv).expanduser().resolve() if venv else _default_venv_dir(project_dir)

    _print_header("Setup de proyecto externo")
    print(f"Proyecto : {project_dir}")
    print(f"Venv     : {venv_dir}")

    py_cmd = shutil.which("python") or shutil.which("python3")
    if not py_cmd:
        print("[ERROR] Python no encontrado en PATH.")
        return 1

    if not venv_dir.exists():
        print("\nCreando entorno virtual...")
        _run([py_cmd, "-m", "venv", str(venv_dir)])
    else:
        print("\nEntorno virtual ya existe, se reutilizara.")

    venv_python = _python_in_venv(venv_dir)
    if not venv_python.exists():
        print(f"[ERROR] No se encontro python dentro del venv: {venv_python}")
        return 1

    if with_pip_upgrade:
        print("\nActualizando pip...")
        _run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"])

    req_paths: list[Path] = []
    if requirements:
        for req in requirements:
            req_path = Path(req).expanduser().resolve()
            if not req_path.exists():
                print(f"[ERROR] requirements no encontrado: {req_path}")
                return 1
            req_paths.append(req_path)
    else:
        req_paths = _detect_requirements(project_dir)

    if req_paths:
        print("\nInstalando dependencias:")
        for req_path in req_paths:
            print(f"- {req_path}")
            _run([str(venv_python), "-m", "pip", "install", "-r", str(req_path)], cwd=project_dir)
    else:
        print("\nNo se detectaron archivos requirements*.txt; solo se creo el entorno virtual.")

    print("\nListo. Activa el entorno con:")
    if os.name == "nt":
        print(f"  {venv_dir}\\Scripts\\activate")
    else:
        print(f"  source {venv_dir}/bin/activate")
    return 0


def _op_read(secret_ref: str) -> str:
    op_executable = _resolve_op_executable()
    if not op_executable:
        raise RuntimeError("op (1Password CLI) no esta disponible")
    completed = subprocess.run([op_executable, "read", secret_ref], capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or "Error desconocido leyendo secreto en 1Password"
        raise RuntimeError(stderr)
    return completed.stdout.strip()


def command_ssh_init(vault: str, item: str, key_name: str, private_field: str, public_field: str, force: bool) -> int:
    _print_header("Inicializacion SSH desde 1Password")

    if not _require_1password_session():
        return 1

    private_ref = f"op://{vault}/{item}/{private_field}"
    public_ref = f"op://{vault}/{item}/{public_field}"

    try:
        private_key = _op_read(private_ref)
        public_key = _op_read(public_ref)
    except RuntimeError as exc:
        print(f"[ERROR] No se pudo leer la llave desde 1Password: {exc}")
        return 1

    if "BEGIN OPENSSH PRIVATE KEY" not in private_key:
        print("[ERROR] El campo privado no parece una llave SSH valida.")
        print(f"Revisa referencia: {private_ref}")
        return 1

    if not (public_key.startswith("ssh-") or "ssh-" in public_key):
        print("[ERROR] El campo publico no parece una llave SSH valida.")
        print(f"Revisa referencia: {public_ref}")
        return 1

    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(parents=True, exist_ok=True)
    key_path = ssh_dir / key_name
    pub_key_path = key_path.with_suffix(".pub")

    if (key_path.exists() or pub_key_path.exists()) and not force:
        print(f"[ERROR] Ya existe una llave con nombre {key_name} en {ssh_dir}")
        print("Usa --force para sobrescribirla conscientemente.")
        return 1

    key_path.write_text(private_key + "\n", encoding="utf-8")
    pub_key_path.write_text(public_key + "\n", encoding="utf-8")

    # Ajuste de permisos cuando el sistema lo soporta.
    if os.name != "nt":
        key_path.chmod(0o600)
        pub_key_path.chmod(0o644)

    print("\nLlaves SSH instaladas desde 1Password:")
    print(f"- Privada: {key_path}")
    print(f"- Publica: {pub_key_path}")
    print("\nSiguiente paso:")
    print(f"1. Cargar en agente SSH: ssh-add {key_path}")
    print("2. Verificar conexion: ssh -T git@github.com")
    return 0


def command_token_check(tokens: list[str]) -> int:
    _print_header("Validacion de tokens por entorno")

    if not tokens:
        tokens = ["GITHUB_TOKEN", "DBCODE_TOKEN", "OPENAI_API_KEY"]

    missing = 0
    for token_name in tokens:
        value = os.environ.get(token_name, "")
        if value:
            masked = value[:3] + "..." + value[-3:] if len(value) >= 8 else "***"
            print(f"- {token_name:<20} OK ({masked})")
        else:
            print(f"- {token_name:<20} FALTA")
            missing += 1

    print("\nNota de seguridad: usa 1Password/gestor de secretos y exporta variables por sesion.")
    return 1 if missing else 0


def _build_tunnel_command(user: str, host: str, local_port: int, remote_host: str, remote_port: int, identity_file: str | None) -> list[str]:
    cmd = [
        "ssh",
        "-N",
        "-L",
        f"{local_port}:{remote_host}:{remote_port}",
        f"{user}@{host}",
    ]
    if identity_file:
        cmd[1:1] = ["-i", identity_file]
    return cmd


def command_dbcode_tunnel(
    user: str,
    host: str,
    local_port: int,
    remote_host: str,
    remote_port: int,
    identity_file: str | None,
    execute: bool,
) -> int:
    _print_header("Tunnel SSH para DBCode")

    if not _require_1password_session():
        print("Login SSH permitido solo via 1Password.")
        return 1

    if not shutil.which("ssh"):
        print("[ERROR] ssh no esta disponible.")
        return 1

    cmd = _build_tunnel_command(user, host, local_port, remote_host, remote_port, identity_file)
    printable = " ".join(shlex.quote(part) for part in cmd)

    print("Comando del tunnel:")
    print(f"  {printable}")
    print("\nConfigura DBCode para conectar a localhost y el puerto local elegido.")

    if not execute:
        print("\nModo preview: agrega --execute para abrir el tunnel ahora.")
        return 0

    print("\nAbriendo tunnel (Ctrl+C para cerrar)...")
    return _run(cmd, check=False)


def command_setup_claude_key(
    vault: str = "Data Analytics",
    item: str = "Claude",
    field: str = "credencial",
) -> int:
    _print_header("Configurar API Key de Claude")

    if not _require_1password_session():
        return 1

    op_executable = _resolve_op_executable()
    reference = f"op://{vault}/{item}/{field}"
    print(f"Leyendo key desde 1Password: {reference}")

    result = subprocess.run(
        [op_executable, "read", "--no-newline", reference],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        print(f"[ERROR] No se pudo leer el campo desde 1Password.")
        if result.stderr:
            print(result.stderr.strip())
        return 1

    api_key = result.stdout.strip()

    if os.name == "nt":
        completed = subprocess.run(
            ["setx", "ANTHROPIC_API_KEY", api_key],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            print("[ERROR] No se pudo setear la variable con setx.")
            print(completed.stderr.strip())
            return 1
        print("ANTHROPIC_API_KEY seteada como variable de entorno de usuario.")
        print("Reinicia VS Code para que tome el nuevo valor.")
    else:
        profile_file = Path.home() / ".zshrc"
        if not profile_file.exists():
            profile_file = Path.home() / ".bashrc"
        marker = "# ANTHROPIC_API_KEY (personal-starter)"
        content = profile_file.read_text(encoding="utf-8") if profile_file.exists() else ""
        lines = [l for l in content.splitlines() if marker not in l and "ANTHROPIC_API_KEY" not in l]
        lines.append(f'{marker}\nexport ANTHROPIC_API_KEY="{api_key}"')
        profile_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"ANTHROPIC_API_KEY escrita en {profile_file}")
        print(f"Ejecuta 'source {profile_file}' o reinicia la terminal.")

    return 0


def command_zstd_passthrough(args: list[str]) -> int:
    if not ZSTD_SCRIPT.exists():
        print(f"[ERROR] No se encontro {ZSTD_SCRIPT}")
        return 1
    return _run([sys.executable, str(ZSTD_SCRIPT), *args], check=False)


def menu() -> int:
    while True:
        print()
        print("╔══════════════════════════════════════════════════════╗")
        print("║       PERSONAL STARTER — Toolbox de Proyectos       ║")
        print("╠══════════════════════════════════════════════════════╣")
        print("║  1  ▶  Abrir herramienta zstd (menu original)        ║")
        print("║  2  ▶  Setup entorno de otro proyecto                ║")
        print("║  3  ▶  Revisar tokens por variables de entorno       ║")
        print("║  4  ▶  Instalar llave SSH desde 1Password            ║")
        print("║  5  ▶  Generar comando de tunnel DBCode              ║")
        print("║  6  ▶  Doctor (python/git/ssh/code)                 ║")
        print("║  7  ▶  Configurar API Key de Claude (1Password)      ║")
        print("║  0  ▶  Salir                                         ║")
        print("╚══════════════════════════════════════════════════════╝")

        option = input("\n  Opcion: ").strip()

        if option == "1":
            command_zstd_passthrough([])
        elif option == "2":
            project = input("  Ruta del proyecto: ").strip()
            if not project:
                print("  [ERROR] Debes indicar una ruta.")
                continue
            command_setup_project(project=project, venv=None, requirements=[], with_pip_upgrade=True)
        elif option == "3":
            raw = input("  Variables separadas por coma [GITHUB_TOKEN,DBCODE_TOKEN,OPENAI_API_KEY]: ").strip()
            tokens = [part.strip() for part in raw.split(",") if part.strip()] if raw else []
            command_token_check(tokens)
        elif option == "4":
            vault = input("  Vault de 1Password: ").strip()
            item = input("  Item de 1Password: ").strip()
            if not vault or not item:
                print("  [ERROR] Vault e item son obligatorios.")
                continue
            key_name = input("  Nombre de la llave [id_ed25519]: ").strip() or "id_ed25519"
            command_ssh_init(
                vault=vault,
                item=item,
                key_name=key_name,
                private_field="private key",
                public_field="public key",
                force=False,
            )
        elif option == "5":
            user = input("  Usuario SSH: ").strip()
            host = input("  Host SSH (bastion/vm): ").strip()
            remote_host = input("  Host remoto de DB [127.0.0.1]: ").strip() or "127.0.0.1"
            try:
                remote_port = int(input("  Puerto remoto DB [5432]: ").strip() or "5432")
                local_port = int(input("  Puerto local [15432]: ").strip() or "15432")
            except ValueError:
                print("  [ERROR] Puerto invalido.")
                continue
            if not user or not host:
                print("  [ERROR] Usuario y host son obligatorios.")
                continue
            command_dbcode_tunnel(
                user=user,
                host=host,
                local_port=local_port,
                remote_host=remote_host,
                remote_port=remote_port,
                identity_file=None,
                execute=False,
            )
        elif option == "6":
            command_doctor()
        elif option == "7":
            command_setup_claude_key()
        elif option == "0":
            return 0
        else:
            print("  [ERROR] Opcion no valida.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Starter toolbox para desarrollo local y conexiones seguras",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("menu", help="Abrir menu interactivo")
    sub.add_parser("doctor", help="Validar herramientas base del entorno")

    setup = sub.add_parser("setup-project", help="Crear venv e instalar requirements de otro proyecto")
    setup.add_argument("project", help="Ruta del proyecto objetivo")
    setup.add_argument("--venv", default=None, help="Ruta del venv (default: <project>/.venv)")
    setup.add_argument("--requirements", "-r", action="append", default=[], help="Archivo requirements adicional")
    setup.add_argument("--skip-pip-upgrade", action="store_true", help="No actualizar pip")

    ssh_init = sub.add_parser("ssh-init", help="Instalar llave SSH desde 1Password")
    ssh_init.add_argument("--vault", required=True, help="Nombre del vault en 1Password")
    ssh_init.add_argument("--item", required=True, help="Nombre del item en 1Password")
    ssh_init.add_argument("--key-name", default="id_ed25519", help="Nombre de la llave en ~/.ssh")
    ssh_init.add_argument("--private-field", default="private key", help="Nombre del campo de llave privada")
    ssh_init.add_argument("--public-field", default="public key", help="Nombre del campo de llave publica")
    ssh_init.add_argument("--force", action="store_true", help="Sobrescribir si ya existe")

    token_check = sub.add_parser("token-check", help="Validar que existan variables de token")
    token_check.add_argument("--token", action="append", default=[], help="Nombre de variable de entorno")

    tunnel = sub.add_parser("dbcode-tunnel", help="Generar o abrir tunnel SSH para DBCode")
    tunnel.add_argument("--user", required=True, help="Usuario SSH")
    tunnel.add_argument("--host", required=True, help="Host SSH (bastion o VM)")
    tunnel.add_argument("--local-port", type=int, default=15432, help="Puerto local para DBCode")
    tunnel.add_argument("--remote-host", default="127.0.0.1", help="Host de base de datos desde el servidor SSH")
    tunnel.add_argument("--remote-port", type=int, required=True, help="Puerto remoto de base de datos")
    tunnel.add_argument("--identity-file", default=None, help="Llave privada SSH opcional")
    tunnel.add_argument("--execute", action="store_true", help="Ejecutar tunnel en primer plano")

    claude_key = sub.add_parser("setup-claude-key", help="Leer API Key de Claude desde 1Password y setearla como variable de entorno")
    claude_key.add_argument("--vault", default="Data Analytics", help="Vault de 1Password (default: Data Analytics)")
    claude_key.add_argument("--item", default="Claude", help="Item de 1Password (default: Claude)")
    claude_key.add_argument("--field", default="credencial", help="Campo del item (default: credencial)")

    zstd = sub.add_parser("zstd", help="Passthrough a zstd_project.py")
    zstd.add_argument("zstd_args", nargs=argparse.REMAINDER, help="Argumentos para zstd_project.py")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command or args.command == "menu":
        return menu()

    if args.command == "doctor":
        return command_doctor()

    if args.command == "setup-project":
        return command_setup_project(
            project=args.project,
            venv=args.venv,
            requirements=args.requirements,
            with_pip_upgrade=not args.skip_pip_upgrade,
        )

    if args.command == "ssh-init":
        return command_ssh_init(
            vault=args.vault,
            item=args.item,
            key_name=args.key_name,
            private_field=args.private_field,
            public_field=args.public_field,
            force=args.force,
        )

    if args.command == "token-check":
        return command_token_check(tokens=args.token)

    if args.command == "dbcode-tunnel":
        return command_dbcode_tunnel(
            user=args.user,
            host=args.host,
            local_port=args.local_port,
            remote_host=args.remote_host,
            remote_port=args.remote_port,
            identity_file=args.identity_file,
            execute=args.execute,
        )

    if args.command == "setup-claude-key":
        return command_setup_claude_key(vault=args.vault, item=args.item, field=args.field)

    if args.command == "zstd":
        return command_zstd_passthrough(args.zstd_args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
