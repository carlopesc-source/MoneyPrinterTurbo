#!/usr/bin/env bash
# Muestra rápida: solo los 2 primeros bloques del guion (unos 45 segundos).
#
# Uso:
#   bash projects/hombre-que-lo-consiguio-todo/run_prueba.sh          # vídeo de muestra
#   bash projects/hombre-que-lo-consiguio-todo/run_prueba.sh audio    # solo la voz
#
# Equivalente en Windows: doble clic en prueba.bat
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ETAPA="${1:-video}"

exec python3 "$DIR/hacer_video.py" --prueba --parar-en "$ETAPA"
