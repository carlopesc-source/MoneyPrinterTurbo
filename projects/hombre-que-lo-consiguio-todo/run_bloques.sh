#!/usr/bin/env bash
# Vídeo entero: los 12 bloques del guion y el MP4 final unido.
#
# Cada bloque busca sus propios términos en Pexels, así que las imágenes
# corresponden al tramo del guion que se está narrando. Es la única forma, con
# este pipeline, de fijar imagen a sección.
#
# Uso:
#   bash projects/hombre-que-lo-consiguio-todo/run_bloques.sh
#
# Equivalente en Windows: doble clic en completo.bat
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec python3 "$DIR/hacer_video.py" "$@"
