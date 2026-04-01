@echo off
REM Entrypoint simplificado — delega a Python bootstrap
python "%~dp0scripts\bootstrap.py" %*
