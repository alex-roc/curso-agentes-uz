#!/usr/bin/env bash
# Instalador del curso (macOS, Linux y Git Bash en Windows): `bash instalar.sh`
# Deja instalado uv, las dependencias y el entorno, y lanza el configurador de tu modelo.
set -euo pipefail
cd "$(dirname "$0")"

echo "== Curso «Más allá de los chatbots»: instalación =="

if ! command -v git >/dev/null 2>&1; then
  echo "Aviso: no encuentro git. No hace falta para ejecutar el curso, pero sí para actualizar el repositorio (https://git-scm.com/downloads)."
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "No encuentro uv, el gestor de Python del curso. Lo voy a instalar con el instalador oficial de Astral"
  echo "(https://astral.sh/uv/install.sh); se instala en tu carpeta de usuario, sin permisos de administrador."
  if [ -t 0 ] && [ -z "${INSTALAR_SI:-}" ]; then
    read -r -p "¿Continuar? [S/n] " r
    case "${r:-s}" in [sSyY]*) ;; *) echo "Cancelado."; exit 1 ;; esac
  fi
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # uv se instala en ~/.local/bin (o ~/.cargo/bin en versiones antiguas)
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
  command -v uv >/dev/null 2>&1 || { echo "uv se instaló pero esta terminal no lo ve: ciérrala, ábrela y repite."; exit 1; }
fi

echo "Instalando Python 3.12 y las dependencias (la primera vez tarda unos minutos)..."
uv sync

echo
uv run python -m utilidades.configurar "$@"
