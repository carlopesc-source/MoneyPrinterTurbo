# El hombre que lo consiguió todo

Guion y configuración de render para el vídeo de ~9 minutos, listo para
ejecutar con el CLI de este repo.

## Ficheros

| Fichero | Qué es |
|---|---|
| `guion.md` | **Fuente de verdad.** Guion por bloques, con marcas de tiempo y términos de búsqueda. Es el único fichero que se edita a mano. |
| `construir_bloques.py` | Regenera `guion.txt`, `terminos.txt` y `bloques.jsonl` a partir de `guion.md`, e imprime la duración estimada de cada bloque. |
| `hacer_video.py` | **El que hace todo.** Comprueba la clave, regenera los ficheros, lanza los bloques y une el MP4 final. No hay que pegar nada a mano. |
| `prueba.bat`, `completo.bat` | Windows: doble clic. Llaman a `hacer_video.py` con el Python del proyecto. |
| `run_prueba.sh`, `run_bloques.sh` | Lo mismo en Linux/Mac. Son envoltorios de `hacer_video.py`. |
| `WINDOWS.md` | Cómo traerse esta rama desde GitHub y hacer el vídeo en Windows, paso a paso. |
| `personaje_daniel.md` | Qué se puede y qué no se puede hacer con Daniel dibujado, y el plano a plano. |
| `animatica/` | Dibuja los 87 planos de Daniel y monta el vídeo con ellos, sin Pexels ni imágenes externas. Para ver el montaje antes de encargar arte. |
| `guion.txt`, `terminos.txt`, `bloques.jsonl` | Generados. No los edites: se sobrescriben. |

## 0. La vía corta

En Windows, doble clic en `prueba.bat` (muestra de 45 s) o en `completo.bat`
(vídeo entero). En Linux o Mac:

```bash
python3 projects/hombre-que-lo-consiguio-todo/hacer_video.py --prueba
python3 projects/hombre-que-lo-consiguio-todo/hacer_video.py
```

Se encarga de todo: comprueba `config.toml`, pide la clave de Pexels la primera
vez si falta, regenera los ficheros derivados, renderiza bloque a bloque y une
el resultado. El resto de este documento es para entender qué hace por dentro.

## 1. Configuración

La clave de Pexels va en `config.toml`, que está en `.gitignore` y **no se
sube al repositorio**. `hacer_video.py` lo crea y lo rellena solo la primera
vez, así que este paso solo hace falta si prefieres hacerlo a mano:

```bash
cp config.example.toml config.toml
```

Y dentro, en la sección `[app]`:

```toml
pexels_api_keys = ["TU_CLAVE_DE_PEXELS"]
video_source = "pexels"
subtitle_provider = "edge"
```

No hace falta ninguna clave de LLM: al pasar el guion y los términos ya
escritos, `generate_script` y `generate_terms` no llaman al modelo
(`app/services/task.py:288` y `:309`). Con Pexels y Edge TTS es suficiente.

## 2. Medir la duración real antes de renderizar

La estimación de `construir_bloques.py` es aritmética (palabras entre 2,8), no
una medición. La duración real es la del audio que genera el TTS:

```bash
bash projects/hombre-que-lo-consiguio-todo/run_prueba.sh audio
```

Imprime `audio_duration` en segundos. Con el guion actual la estimación son
499 s (8:19); la duración real depende de la voz y suele quedar algo por
encima. Si te alejas mucho de los 9:00, ajusta texto en `guion.md` y vuelve a
medir: renderizar el vídeo entero para descubrir que dura 7 minutos cuesta
mucho más tiempo.

## 3. Renderizar

**Prueba rápida** (una tarea, guion entero):

```bash
bash projects/hombre-que-lo-consiguio-todo/run_prueba.sh
```

**Versión por bloques** (12 tareas + concatenado):

```bash
bash projects/hombre-que-lo-consiguio-todo/run_bloques.sh
```

La salida queda en `projects/hombre-que-lo-consiguio-todo/salida/`.

## Por qué existen dos scripts

En una sola tarea, `_download_videos_by_script_order`
(`app/services/material.py:1475`) reparte los términos en **round-robin**:
primera vuelta, el primer resultado de cada término; segunda vuelta, el
segundo de cada término. El resultado es que las imágenes van rotando por
todos los términos del vídeo entero, así que **la imagen no se corresponde con
el tramo que se está narrando**. Para un vídeo de 9 minutos con estructura,
eso se ve.

`run_bloques.sh` resuelve eso por la vía directa: cada bloque es una tarea
independiente con sus propios términos, así que sus imágenes solo pueden salir
de su propio bloque. Luego se unen los 12 MP4 con el demuxer `concat` de
ffmpeg, sin recodificar.

Coste: la música de fondo va desactivada en los bloques
(`bgm_type` vacío), porque si no se reiniciaría en cada uno. Si quieres
música, ponla sobre el fichero concatenado.

## Decisiones que están tomadas en los ficheros

- **Voz:** `es-ES-AlvaroNeural-Male`. Cámbiala en `construir_bloques.py`
  (constante `VOZ`) y en `run_prueba.sh`. El catálogo completo está en
  `app/services/data/azure_voices.json`: hay 45 voces en español, incluidas
  `es-MX-JorgeNeural`, `es-AR-TomasNeural` y `es-US-AlonsoNeural`.
- **Fuente de subtítulos:** `BeVietnamPro-Bold.ttf`, la única de
  `resource/fonts/` que se ha comprobado que trae todos los caracteres
  españoles (á é í ó ú ü ñ ¿ ¡ « » —). La de por defecto, `STHeitiMedium.ttc`,
  es una fuente china.
- **Formato:** 16:9, porque son 9 minutos. Para vertical, cambia
  `video_aspect` a `9:16`.
- **Clips de 6 s**, para bajar el número de cortes de ~100 a ~84.

## Sobre el dato psicológico

El guion no da la explicación como clase: el hombre del taller la va sacando
de los recuerdos de Daniel, y el término "adaptación hedónica" aparece **una
sola vez, en el minuto 8:30**, cuando ya la ha vivido entera.

Por eso mismo, el guion **no contiene ni una cifra, ni un porcentaje, ni un
estudio citado**. Es deliberado: cualquier dato de ese tipo habría que
verificarlo en la fuente primaria antes de publicarlo, y una cifra inventada
en un vídeo divulgativo es un problema que no se arregla luego.
