#!/usr/bin/env bash
# Prueba rápida: una sola tarea con el guion entero.
#
# Uso:
#   bash projects/hombre-que-lo-consiguio-todo/run_prueba.sh            # vídeo completo
#   bash projects/hombre-que-lo-consiguio-todo/run_prueba.sh audio      # solo TTS, para medir duración
#
# Se ejecuta desde la raíz del repo. Requiere pexels_api_keys en config.toml.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$(cd "$DIR/../.." && pwd)"
ETAPA="${1:-video}"

cd "$RAIZ"
python3 "$DIR/construir_bloques.py" >/dev/null

exec python3 cli.py \
  --video-subject "El hombre que lo consiguió todo" \
  --video-script "$(cat "$DIR/guion.txt")" \
  --video-terms "$(cat "$DIR/terminos.txt")" \
  --video-source pexels \
  --video-aspect 16:9 \
  --video-clip-duration 6 \
  --match-materials-to-script \
  --voice-name "es-ES-AlvaroNeural-Male" \
  --font-name "BeVietnamPro-Bold.ttf" \
  --font-size 48 \
  --subtitle-position bottom \
  --bgm-type none \
  --stop-at "$ETAPA"
