#!/usr/bin/env bash
# Render por bloques: 12 tareas (una por bloque de la escaleta) y concatenado final.
#
# A diferencia de run_prueba.sh, aquí cada bloque busca sus propios términos en
# Pexels, así que las imágenes corresponden al tramo del guion que se está
# narrando. Es la única forma, con este pipeline, de fijar imagen a sección.
#
# Uso:
#   bash projects/hombre-que-lo-consiguio-todo/run_bloques.sh
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$(cd "$DIR/../.." && pwd)"
SALIDA="$DIR/salida"

cd "$RAIZ"
mkdir -p "$SALIDA"
python3 "$DIR/construir_bloques.py"

python3 cli.py --batch-file "$DIR/bloques.jsonl" --stop-at video \
  | tee "$SALIDA/resumen.json"

python3 - "$SALIDA/resumen.json" "$SALIDA/lista.txt" <<'PY'
import json
import sys

resumen = json.load(open(sys.argv[1], encoding="utf-8"))
fallidas = [t for t in resumen["tasks"] if t["status"] != "succeeded"]
if fallidas:
    for t in fallidas:
        print(f"tarea {t['index']} falló en {t['failed_stage']}: {t['error']}",
              file=sys.stderr)
    raise SystemExit("hay bloques fallidos; no se concatena nada")

rutas = []
for tarea in sorted(resumen["tasks"], key=lambda t: t["index"]):
    videos = (tarea.get("result") or {}).get("videos") or []
    if not videos:
        raise SystemExit(f"la tarea {tarea['index']} no devolvió ningún vídeo")
    rutas.append(videos[0])

with open(sys.argv[2], "w", encoding="utf-8") as lista:
    for ruta in rutas:
        lista.write("file '%s'\n" % ruta.replace("'", r"'\''"))
print(f"{len(rutas)} bloques listos para concatenar")
PY

# Todos los bloques salen con los mismos parámetros de códec, así que se pueden
# unir sin recodificar. Si ffmpeg se queja, quita "-c copy" para recodificar.
ffmpeg -y -f concat -safe 0 -i "$SALIDA/lista.txt" -c copy \
  "$SALIDA/hombre-que-lo-consiguio-todo.mp4"

echo "vídeo final: $SALIDA/hombre-que-lo-consiguio-todo.mp4"
