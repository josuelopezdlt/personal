#!/usr/bin/env bash
# Entrypoint simplificado — delega a Python bootstrap
python3 "$(dirname "$0")/scripts/bootstrap.py" "$@"
