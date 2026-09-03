#!/usr/bin/env python3
"""Genera el vídeo completo sin pegar nada a mano.

Hace, en orden, lo que antes había que teclear:

  1. Comprueba que existe config.toml y que tiene la clave de Pexels.
  2. Regenera guion.txt, terminos.txt y bloques.jsonl a partir de guion.md.
  3. Lanza cli.py con el manifiesto de bloques.
  4. Une los bloques en un único MP4 con ffmpeg.

Uso (desde cualquier sitio):

  python hacer_video.py --prueba          # solo los 2 primeros bloques (~45 s)
  python hacer_video.py                   # los 12 bloques y el vídeo final
  python hacer_video.py --bloques 3 4 5   # solo esos bloques
  python hacer_video.py --parar-en audio  # solo la voz, para medir duración

En Windows no hace falta escribir nada: doble clic en prueba.bat o completo.bat.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import NoReturn

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
SALIDA = AQUI / "salida"

if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))


def aviso(texto: str) -> None:
    print(f"\n>>> {texto}", flush=True)


def error(texto: str) -> NoReturn:
    print(f"\n!!! {texto}\n", file=sys.stderr, flush=True)
    esperar_tecla()
    raise SystemExit(1)


def esperar_tecla() -> None:
    """En Windows la ventana se cierra sola; sin esto no da tiempo a leer nada."""
    if os.name == "nt" and sys.stdin is not None and sys.stdin.isatty():
        try:
            input("\nPulsa Intro para cerrar esta ventana...")
        except (EOFError, KeyboardInterrupt):
            pass


def interprete_del_proyecto() -> Path | None:
    """Devuelve el Python que tiene instaladas las dependencias, si lo encuentra.

    Mismo orden que webui.bat: primero el entorno virtual del repo, luego el
    Python que trae dentro el paquete de un clic de Windows.
    """
    candidatos = [
        RAIZ / ".venv" / "Scripts" / "python.exe",
        RAIZ / ".venv" / "bin" / "python",
        RAIZ / "lib" / "python" / "python.exe",
    ]
    for candidato in candidatos:
        if candidato.exists():
            return candidato
    return None


def asegurar_dependencias() -> None:
    """Si nos han lanzado con un Python sin dependencias, reintenta con el bueno.

    Pasa a menudo: en Windows se abre el fichero con el Python del sistema en vez
    del que trae el proyecto, y el error que sale ("No module named 'loguru'") no
    dice nada de lo que de verdad hay que hacer.
    """
    try:
        import loguru  # noqa: F401

        return
    except ImportError:
        pass

    if os.environ.get("HACER_VIDEO_RELANZADO"):
        error(
            "las dependencias no están instaladas en este Python.\n"
            f"    Python usado: {sys.executable}\n"
            "    Instálalas desde la carpeta del proyecto con:  uv sync --frozen"
        )

    otro = interprete_del_proyecto()
    # Sin resolve(): en un entorno virtual .venv/bin/python es un enlace al
    # intérprete del sistema, así que resolverlo haría creer que son el mismo.
    if otro is None or Path(sys.executable) == otro:
        error(
            "faltan las dependencias del proyecto y no encuentro su entorno.\n"
            "    Instálalas desde la carpeta del proyecto con:  uv sync --frozen"
        )

    aviso(f"cambiando al Python del proyecto: {otro}")
    entorno = dict(os.environ, HACER_VIDEO_RELANZADO="1", PYTHONPATH=str(RAIZ))
    completado = subprocess.run(
        [str(otro), str(Path(__file__).resolve()), *sys.argv[1:]],
        cwd=RAIZ,
        env=entorno,
    )
    raise SystemExit(completado.returncode)


def asegurar_config(clave: str | None) -> None:
    """config.toml tiene que existir y llevar dentro la clave de Pexels.

    La clave se guarda en config.toml, que está en .gitignore: no viaja a GitHub
    aunque hagas commit. Por eso no está escrita dentro de este fichero.
    """
    config = RAIZ / "config.toml"
    ejemplo = RAIZ / "config.example.toml"

    if not config.exists():
        if not ejemplo.exists():
            error(f"no encuentro {ejemplo}; ¿está completa la copia del repo?")
        shutil.copy2(ejemplo, config)
        aviso(f"he creado {config} a partir del ejemplo")

    texto = config.read_text(encoding="utf-8")
    actual = re.search(r"^pexels_api_keys\s*=\s*(.+)$", texto, re.MULTILINE)
    if actual is None:
        error(
            "config.toml no tiene la línea pexels_api_keys. "
            "Bórralo y vuelve a lanzar esto para regenerarlo desde el ejemplo."
        )

    ya_tiene = bool(re.search(r'"[^"\s]{10,}"', actual.group(1)))
    if ya_tiene and not clave:
        return

    if not clave:
        clave = os.environ.get("PEXELS_API_KEY", "").strip()
    if not clave:
        print(
            "\nFalta la clave de Pexels (gratis en https://www.pexels.com/api/).\n"
            "Se guarda en config.toml y no se sube a GitHub.\n"
        )
        try:
            clave = input("Pega aquí tu clave de Pexels y pulsa Intro: ").strip()
        except (EOFError, KeyboardInterrupt):
            clave = ""
    if not clave:
        error("sin clave de Pexels no se puede descargar material de vídeo")

    nuevo = re.sub(
        r"^pexels_api_keys\s*=\s*.+$",
        f'pexels_api_keys = ["{clave}"]',
        texto,
        count=1,
        flags=re.MULTILINE,
    )
    config.write_text(nuevo, encoding="utf-8")
    aviso("clave de Pexels guardada en config.toml")


def construir() -> list[dict]:
    """Regenera los ficheros derivados y devuelve las tareas del manifiesto."""
    aviso("regenerando guion.txt, terminos.txt y bloques.jsonl desde guion.md")
    subprocess.run(
        [sys.executable, str(AQUI / "construir_bloques.py")],
        cwd=RAIZ,
        check=True,
    )
    manifiesto = AQUI / "bloques.jsonl"
    tareas = [
        json.loads(linea)
        for linea in manifiesto.read_text(encoding="utf-8").splitlines()
        if linea.strip()
    ]
    if not tareas:
        error(f"{manifiesto} ha salido vacío")
    return tareas


def seleccionar(tareas: list[dict], indices: list[int] | None) -> Path:
    """Escribe el manifiesto que se le va a pasar a cli.py."""
    if indices:
        fuera = [n for n in indices if n < 1 or n > len(tareas)]
        if fuera:
            error(f"bloques inexistentes: {fuera} (hay {len(tareas)})")
        elegidas = [tareas[n - 1] for n in indices]
    else:
        elegidas = tareas

    SALIDA.mkdir(parents=True, exist_ok=True)
    destino = SALIDA / "tareas.jsonl"
    with destino.open("w", encoding="utf-8") as fichero:
        for tarea in elegidas:
            fichero.write(json.dumps(tarea, ensure_ascii=False) + "\n")
    aviso(f"{len(elegidas)} bloque(s) a renderizar")
    return destino


def extraer_resumen(lineas: list[str]) -> dict | None:
    """Saca el resumen JSON de la salida de cli.py.

    cli.py mezcla en la misma salida los mensajes de loguru y el resumen final en
    JSON, así que no vale con parsear todo el bloque: hay que buscar, del final
    hacia atrás, la última línea que sea un JSON con la lista de tareas dentro.
    """
    for linea in reversed(lineas):
        recortada = linea.strip()
        if not recortada.startswith("{"):
            continue
        try:
            candidato = json.loads(recortada)
        except json.JSONDecodeError:
            continue
        if isinstance(candidato, dict) and "tasks" in candidato:
            return candidato
    return None


def ejecutar(manifiesto: Path, parar_en: str) -> dict:
    """Lanza cli.py mostrando el progreso en directo y guardando el registro."""
    aviso("arrancando el render; abajo va saliendo el progreso")
    registro = SALIDA / "registro.txt"
    lineas: list[str] = []

    proceso = subprocess.Popen(
        [
            sys.executable,
            "cli.py",
            "--batch-file",
            str(manifiesto),
            "--stop-at",
            parar_en,
        ],
        cwd=RAIZ,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )
    assert proceso.stdout is not None
    with registro.open("w", encoding="utf-8") as diario:
        for linea in proceso.stdout:
            print(linea, end="", flush=True)
            diario.write(linea)
            lineas.append(linea)
    codigo = proceso.wait()

    resumen = extraer_resumen(lineas)
    if resumen is None:
        error(
            "cli.py ha terminado sin dar un resumen "
            f"(código {codigo}).\n"
            f"    El registro completo está en: {registro}\n"
            "    La causa real está en los últimos mensajes de arriba."
        )
    (SALIDA / "resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return resumen


def rutas_de_video(resumen: dict) -> list[str]:
    fallidas = [t for t in resumen["tasks"] if t["status"] != "succeeded"]
    if fallidas:
        for tarea in fallidas:
            print(
                f"  bloque {tarea['index']} falló en la etapa "
                f"'{tarea.get('failed_stage')}': {tarea.get('error')}",
                file=sys.stderr,
            )
        error("hay bloques fallidos; no se concatena nada")

    rutas = []
    for tarea in sorted(resumen["tasks"], key=lambda t: t["index"]):
        videos = (tarea.get("result") or {}).get("videos") or []
        if not videos:
            error(f"el bloque {tarea['index']} no ha devuelto ningún vídeo")
        rutas.append(videos[0])
    return rutas


def concatenar(rutas: list[str]) -> Path:
    """Une los bloques sin recodificar: todos salen con los mismos códecs."""
    from app.utils.utils import get_ffmpeg_binary

    lista = SALIDA / "lista.txt"
    with lista.open("w", encoding="utf-8") as fichero:
        for ruta in rutas:
            fichero.write("file '%s'\n" % str(ruta).replace("'", r"'\''"))

    final = SALIDA / "hombre-que-lo-consiguio-todo.mp4"
    aviso(f"uniendo {len(rutas)} bloque(s) en {final.name}")
    subprocess.run(
        [
            get_ffmpeg_binary(),
            "-y",
            "-loglevel",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(lista),
            "-c",
            "copy",
            "-movflags",
            "+faststart",
            str(final),
        ],
        check=True,
    )
    return final


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera el vídeo de 'El hombre que lo consiguió todo'."
    )
    parser.add_argument(
        "--prueba",
        action="store_true",
        help="renderiza solo los 2 primeros bloques, para ver una muestra rápida",
    )
    parser.add_argument(
        "--bloques",
        nargs="+",
        type=int,
        metavar="N",
        help="números de bloque a renderizar (1 a 12)",
    )
    parser.add_argument(
        "--parar-en",
        default="video",
        choices=["script", "terms", "audio", "subtitle", "materials", "video"],
        help="detiene la tubería después de esa etapa (por defecto: video)",
    )
    parser.add_argument(
        "--clave-pexels",
        default=None,
        help="clave de Pexels; si se omite se usa la de config.toml",
    )
    args = parser.parse_args()

    if args.prueba and args.bloques:
        error("usa --prueba o --bloques, no las dos")
    indices = [1, 2] if args.prueba else args.bloques

    asegurar_dependencias()
    asegurar_config(args.clave_pexels)
    tareas = construir()
    manifiesto = seleccionar(tareas, indices)
    resumen = ejecutar(manifiesto, args.parar_en)

    if args.parar_en != "video":
        aviso(f"parado en la etapa '{args.parar_en}'. Resumen: {SALIDA / 'resumen.json'}")
        esperar_tecla()
        return

    rutas = rutas_de_video(resumen)
    final = concatenar(rutas)
    aviso(f"LISTO. Vídeo final: {final}")
    esperar_tecla()


if __name__ == "__main__":
    main()
