#!/usr/bin/env python3
"""Convierte guion.md en los ficheros que consume cli.py.

Genera:
  guion.txt     narración completa en texto plano (para una sola tarea)
  terminos.txt  todos los términos de búsqueda, en orden narrativo
  bloques.jsonl manifiesto de --batch-file, una tarea por bloque

Uso:
  python3 projects/hombre-que-lo-consiguio-todo/construir_bloques.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
GUION = BASE / "guion.md"

# Palabras por segundo de la voz en off. Edge TTS en español a voice_rate 1.0
# ronda este valor; sirve solo para estimar antes de renderizar, la duración
# real es la del audio que genera la fase "audio" del pipeline.
PALABRAS_POR_SEGUNDO = 2.8

VOZ = "es-ES-AlvaroNeural-Male"
ASUNTO = "El hombre que lo consiguió todo"

CABECERA = re.compile(r"^##\s*\[(\d{2}:\d{2})-(\d{2}:\d{2})\]\s*(.+?)\s*$")
TERMINOS = re.compile(r"^TERMINOS:\s*(.+?)\s*$")


def parsear(texto: str) -> list[dict]:
    bloques: list[dict] = []
    actual: dict | None = None
    for linea in texto.splitlines():
        cabecera = CABECERA.match(linea)
        if cabecera:
            inicio, fin, titulo = cabecera.groups()
            actual = {
                "inicio": inicio,
                "fin": fin,
                "titulo": titulo,
                "terminos": [],
                "lineas": [],
            }
            bloques.append(actual)
            continue
        if actual is None:
            continue  # preámbulo del fichero
        terminos = TERMINOS.match(linea)
        if terminos:
            actual["terminos"] = [
                t.strip() for t in terminos.group(1).split(",") if t.strip()
            ]
            continue
        if linea.startswith(">"):
            continue  # nota de dirección, no se narra
        actual["lineas"].append(linea)

    for bloque in bloques:
        cuerpo = "\n".join(bloque["lineas"]).strip()
        bloque["texto"] = re.sub(r"\n{3,}", "\n\n", cuerpo)
        del bloque["lineas"]
    return bloques


def segundos(marca: str) -> int:
    minutos, seg = marca.split(":")
    return int(minutos) * 60 + int(seg)


def main() -> None:
    bloques = parsear(GUION.read_text(encoding="utf-8"))
    if not bloques:
        raise SystemExit(f"no se encontró ningún bloque en {GUION}")

    guion_txt = "\n\n".join(b["texto"] for b in bloques) + "\n"
    (BASE / "guion.txt").write_text(guion_txt, encoding="utf-8")

    terminos: list[str] = []
    for bloque in bloques:
        for termino in bloque["terminos"]:
            if termino not in terminos:
                terminos.append(termino)
    (BASE / "terminos.txt").write_text(", ".join(terminos) + "\n", encoding="utf-8")

    tareas = []
    for indice, bloque in enumerate(bloques, start=1):
        if not bloque["terminos"]:
            raise SystemExit(f"bloque {bloque['titulo']!r} sin línea TERMINOS")
        tareas.append(
            {
                "video_subject": f"{ASUNTO} - {indice:02d} {bloque['titulo']}",
                "video_script": bloque["texto"],
                "video_terms": bloque["terminos"],
                "voice_name": VOZ,
                "video_aspect": "16:9",
                "video_clip_duration": 6,
                "match_materials_to_script": True,
                "video_concat_mode": "sequential",
                "font_name": "BeVietnamPro-Bold.ttf",
                "font_size": 48,
                "bgm_type": "",
            }
        )
    with (BASE / "bloques.jsonl").open("w", encoding="utf-8") as salida:
        for tarea in tareas:
            salida.write(json.dumps(tarea, ensure_ascii=False) + "\n")

    print(f"{'bloque':<44} {'palabras':>8} {'est.':>7} {'escaleta':>9}")
    total_palabras = 0
    for bloque in bloques:
        palabras = len(bloque["texto"].split())
        total_palabras += palabras
        estimado = palabras / PALABRAS_POR_SEGUNDO
        objetivo = segundos(bloque["fin"]) - segundos(bloque["inicio"])
        etiqueta = f"[{bloque['inicio']}-{bloque['fin']}] {bloque['titulo']}"
        print(f"{etiqueta:<44} {palabras:>8} {estimado:>6.0f}s {objetivo:>8}s")
    total_estimado = total_palabras / PALABRAS_POR_SEGUNDO
    print(f"{'TOTAL':<44} {total_palabras:>8} {total_estimado:>6.0f}s")
    print(f"\nescrito: guion.txt, terminos.txt, bloques.jsonl ({len(tareas)} tareas)")


if __name__ == "__main__":
    main()
