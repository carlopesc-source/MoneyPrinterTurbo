# Animática: Daniel dibujado

Genera los fotogramas del personaje y monta el vídeo con ellos, sin depender
de Pexels ni de imágenes externas. No sustituye a un ilustrador: es una
animática, es decir, el vídeo entero montado con dibujos planos para ver
ritmo, encuadres y duración antes de invertir en arte definitivo.

## Uso

```bash
# 1. fotogramas (87 planos, unos 20 segundos)
python3 planos.py daniel

# 2. narración + subtítulos, solo si no tienes Edge TTS disponible
python3 voz.py ../guion.txt narracion.wav narracion.srt

# 3. montaje con las funciones reales de app/services/video.py
python3 render.py --salida el-hombre-que-lo-consiguio-todo.mp4
```

Con Edge TTS funcionando (tu máquina), sáltate el paso 2 y usa el pipeline
normal: `run_bloques.sh`. La voz de Edge es incomparablemente mejor.

## Qué hace cada fichero

| Fichero | Qué hace |
|---|---|
| `dibujar.py` | El personaje: silueta de la cabeza con la nariz integrada, curvas Catmull-Rom, párpado caído, y colores intercambiables para pintar al hombre del taller y a los secundarios. |
| `escenas.py` | Catorce fondos planos: ventana de noche, ventana al amanecer, cocina, oficina, coche, taller, taller en verano, calle de pueblo, cama, tren, salón, salón vacío y dos fondos lisos. |
| `planos.py` | La lista de planos: qué fondo, quién sale, con qué cara y a qué escala. De cada plano saca además una versión de plano corto recortada sobre el lienzo supermuestreado, así que no pierde nitidez. |
| `voz.py` | Narración con espeak-ng, offline. Sintetiza frase a frase para conocer la duración exacta de cada una y escribir el SRT sin Whisper. |
| `render.py` | Preprocesa las imágenes en paralelo y monta contra la narración con `app/services/video.py`. El último paso (audio + subtítulos quemados) lo hace ffmpeg con libass, porque sobre 8:41 de vídeo moviepy tardó más de media hora y ffmpeg tarda dos minutos; con `--moviepy` se fuerza el `generate_video()` del repo, que además mezcla música de fondo. |

## Cambiar un plano

Los planos están en la lista `PLANOS` de `planos.py`:

```python
("05b-taller-puerta", "taller", [("d", 420, 860, 1.9, False, "normal", "neutra"),
                                 ("v", 1180, 860, 1.9, True, "cansado", "neutra")], 1.0),
```

Es: nombre, fondo, lista de personajes y un reservado. Cada personaje es
`(quién, x, y, escala, espejado, ojos, boca)`. `quién` puede ser `d` (Daniel),
`v` (el hombre del taller), `a` (el aprendiz) o `d2` (la pareja). Los ojos
aceptan `normal`, `cansado` y `cerrado`; la boca, `neutra`, `abierta` y
`triste`. La `y` se recalcula sola: figura entera si cabe en el encuadre,
plano medio con la cara en el tercio superior si no.

## Límites, dichos claramente

- Es dibujo generado con polígonos, no ilustración. Sirve para ver el montaje.
- Solo hay tres expresiones de ojos y tres de boca. No hay manos, ni piernas,
  ni animación entre fotogramas: cada plano es una imagen fija con un zoom
  lento del 18 %, el que aplica `preprocess_video`.
- La voz de `voz.py` es espeak-ng: robótica. Está ahí porque el endpoint de
  Edge TTS puede estar bloqueado, no porque sea buena. Con Edge disponible,
  `run_bloques.sh` da otra cosa.

## Tiempos medidos

Sobre este guion, en cuatro núcleos:

| Paso | Tiempo |
|---|---|
| 87 imágenes -> clips (4 procesos) | 980 s |
| Montaje de los 87 clips contra 8:41 de narración | 543 s |
| Audio + subtítulos con ffmpeg | ~120 s |
| Audio + subtítulos con moviepy (`--moviepy`) | más de 1800 s, sin terminar |
