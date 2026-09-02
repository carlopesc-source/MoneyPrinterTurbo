# Daniel como personaje ilustrado

## Lo que este repo puede y no puede hacer con el personaje

Comprobado leyendo el código, no supuesto:

- **MoneyPrinterTurbo no dibuja al personaje.** Las fuentes online
  (`pexels`, `pixabay`, `coverr`) son buscadores de vídeo de stock: devuelven
  grabaciones reales de un catálogo. No hay ninguna forma de pedirles "el
  hombre azul con chaleco marrón".
- **Ninguna fuente de este repo acepta una imagen de referencia.** Las fuentes
  generativas (`volcengine_seedance`, `wavespeed`) mandan solo texto a la API;
  no hay parámetro de imagen inicial ni de personaje de referencia en
  `app/services/volcengine_seedance.py` ni en el resto de `app/services/`.
  Es decir: no se puede pedirle a este pipeline coherencia de personaje.
- **Sí acepta imágenes tuyas.** Con `--video-source local`, el pipeline coge
  las imágenes que le des y las convierte en clips (`app/services/video.py`,
  `preprocess_video`).

Conclusión: los fotogramas de Daniel hay que generarlos fuera (con la
herramienta de imagen que uses), y este repo se encarga del montaje, la voz,
los subtítulos y el render.

## Reglas técnicas de las imágenes locales

Todo esto está verificado en el código:

| Regla | Valor | Dónde |
|---|---|---|
| Formatos aceptados | `jpg`, `jpeg`, `png`, `bmp` | `app/models/const.py:35` |
| Lado mínimo | 480 px (tolerancia 10 px); por debajo se descarta | `app/services/video.py:76` |
| Duración de cada imagen | `--video-clip-duration` segundos exactos | `preprocess_video` |
| Efecto aplicado | zoom lento hasta +18 % con clip de 6 s | `preprocess_video` |
| Dónde deben vivir | `storage/local_videos/`; el CLI copia ahí lo que le pases desde otra ruta | `cli.py`, `file_security.resolve_path_within_directory` |

Genera en 1920x1080 para 16:9 y no tendrás recortes ni bandas negras.

## Cuántas imágenes hacen falta

Con la narración actual (unos 500 s) y clips de 6 s: **unas 84 imágenes** para
que no se repita ninguna. Si das menos, el pipeline no deja el vídeo corto:
recicla los clips en bucle hasta cubrir el audio (`combine_videos`). Con 30
imágenes cada una sale unas 3 veces, y se nota.

## La opción realista: híbrida por bloques

`video_source` es un campo por tarea, así que en `bloques.jsonl` cada bloque
puede usar una fuente distinta. Lo razonable:

- **Daniel dibujado** en los bloques donde el personaje es la escena: hook,
  consigue todo, encuentra al hombre del pueblo, primera revelación, segundo
  giro, conclusión.
- **Pexels** en los bloques de textura y de mecanismo: deterioro, adaptación,
  el cerebro convirtiendo lo extraordinario en normal.

Un bloque con imágenes propias se declara así en `bloques.jsonl`:

```json
{"video_subject": "...", "video_script": "...", "video_source": "local",
 "video_materials": [{"provider": "local", "url": "daniel/01-ventana.png", "duration": 0}],
 "video_clip_duration": 6, "voice_name": "es-ES-AlvaroNeural-Male", "video_aspect": "16:9"}
```

Las rutas relativas de un manifiesto se resuelven **respecto a la carpeta del
manifiesto**, así que `daniel/01-ventana.png` es
`projects/hombre-que-lo-consiguio-todo/daniel/01-ventana.png`.

Importante: con `local` el orden de `video_materials` es el orden en pantalla
(pon `video_concat_mode: "sequential"`), y los `video_terms` se ignoran.

## Plano a plano

Guarda tu imagen de referencia en esta carpeta como `daniel-referencia.png`
y pásasela a la herramienta de imagen en cada generación.

Referencia de personaje: hombre adulto de piel azul, pelo oscuro corto,
chaleco marrón sobre polo blanco, estilo de dibujo plano con línea negra
gruesa, fondo claro y liso. Repite esa descripción literal en cada generación
de imagen: es lo único que mantiene la coherencia, porque la coherencia no la
da este repo.

| # | Bloque | Plano |
|---|---|---|
| 01 | Hook | Daniel de pie ante un ventanal grande, de espaldas, ciudad al fondo, expresión no visible |
| 02 | Hook | Primer plano de su cara, mirada neutra, sin sonrisa |
| 03 | Hook | Daniel sentado en el borde de la cama, habitación amplia y vacía |
| 04 | Consigue todo | Daniel joven en una cocina pequeña, escribiendo en una libreta |
| 05 | Consigue todo | Detalle de la libreta con ocho líneas, dos tachadas |
| 06 | Consigue todo | Daniel con abrigo esperando un autobús de noche |
| 07 | Consigue todo | Daniel en una oficina, de pie, mientras alguien le da la mano |
| 08 | Consigue todo | Daniel solo, copa en la mano, mirando la libreta ya tachada entera |
| 09 | Algo no encaja | Daniel en la ventana al amanecer, café en la mano, cara de asombro |
| 10 | Algo no encaja | El mismo plano, misma postura, cara neutra: la repetición es el chiste |
| 11 | Algo no encaja | Daniel cruzando el salón sin mirar la ventana |
| 12 | Deterioro | Daniel en el coche parado, manos en el volante, mirada al frente |
| 13 | Deterioro | Cena de dos, él mirando el móvil, la otra persona mirándole a él |
| 14 | Deterioro | Daniel despierto en la cama, techo, madrugada |
| 15 | Deterioro | Daniel con la libreta abierta por una página en blanco |
| 16 | Pueblo | Calle de pueblo estrecha, Daniel de espaldas, maleta pequeña |
| 17 | Pueblo | Fachada de un taller mecánico viejo con la persiana subida |
| 18 | Pueblo | Interior del taller: hombre mayor de pelo blanco inclinado sobre un motor |
| 19 | Pueblo | Daniel parado en el marco de la puerta, a contraluz |
| 20 | Pueblo | El hombre mayor levantando la vista, gesto de reconocerlo |
| 21 | Primera revelación | Plano corto del hombre mayor hablando, trapo en la mano |
| 22 | Primera revelación | Daniel con la boca a medio abrir, sin respuesta |
| 23 | Primera revelación | Detalle de manos sobre piezas de motor en un banco de trabajo |
| 24 | Adaptación | Flashback: Daniel a los veintitrés tumbado en el suelo de un salón vacío |
| 25 | Adaptación | El mismo salón, ya amueblado, Daniel cruzándolo sin mirar el suelo |
| 26 | Adaptación | Primer plano de su cara escuchando, incómodo |
| 27 | El cerebro | Cocina de noche, nevera iluminada, Daniel de pie escuchando |
| 28 | El cerebro | Detalle de una cicatriz en su antebrazo |
| 29 | El cerebro | Daniel en el tren, cara pegada a la ventanilla, campo pasando |
| 30 | Intenta cambiar | Daniel metiendo ropa en cajas, armario medio vacío |
| 31 | Intenta cambiar | Daniel bajo la ducha fría, hombros encogidos |
| 32 | Intenta cambiar | Daniel apuntando algo en el móvil con la misma cara que en el plano 04 |
| 33 | Intenta cambiar | Piso pequeño sin vista, Daniel sentado, todo ordenado y quieto |
| 34 | Segundo giro | Taller en verano, polvo en la luz, el hombre mayor en la misma silla |
| 35 | Segundo giro | Daniel de pie frente a él, brazos cruzados |
| 36 | Segundo giro | El hombre mayor limpiándose las manos, mirándole de frente |
| 37 | Segundo giro | El hombre mayor pasándole una herramienta a un chaval de unos veinte |
| 38 | Conclusión | Daniel en su casa leyendo, luz de tarde |
| 39 | Conclusión | Daniel caminando por la calle, sin prisa, sin móvil |
| 40 | Conclusión | Cajón abierto con la libreta dentro, cerrada |
| 41 | Frase final | Daniel de espaldas ante la ventana, exactamente el plano 01 |
| 42 | Frase final | Silla vacía junto a la ventana, sin nadie |

Los planos 01 y 41 son el mismo encuadre a propósito: cierran el círculo del
hook. Si generas los 42 y usas `--video-clip-duration 6`, cubres unos 250 s;
el resto lo rellena el bucle de `combine_videos`, o lo completas con Pexels en
los bloques híbridos.
