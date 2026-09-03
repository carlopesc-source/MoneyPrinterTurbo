# Windows: de mi rama a tu ordenador, y de ahí al vídeo

Todo esto se hace **una sola vez**. Después, hacer el vídeo es un doble clic.

---

## 1. Tu repo en la nube

Está aquí:

**https://github.com/carlopesc-source/MoneyPrinterTurbo**

La rama con este trabajo se llama `claude/man-got-everything-wanted-4txhk6`.
En esa página, el desplegable de arriba a la izquierda que pone `main` te deja
cambiar de rama y ver los ficheros.

## 2. Traerte la rama a tu ordenador

Abre PowerShell **dentro de la carpeta de MoneyPrinterTurbo**: entra en la
carpeta con el Explorador de Windows, haz clic en la barra de direcciones,
escribe `powershell` y pulsa Intro. Se abre ya en el sitio correcto.

Primero comprueba de dónde clonaste:

```powershell
git remote -v
```

**Caso A — pone `carlopesc-source/MoneyPrinterTurbo`:**

```powershell
git fetch origin claude/man-got-everything-wanted-4txhk6
git checkout claude/man-got-everything-wanted-4txhk6
```

**Caso B — pone `harry0703/MoneyPrinterTurbo`** (el repo original, no el tuyo):

```powershell
git remote add mio https://github.com/carlopesc-source/MoneyPrinterTurbo
git fetch mio claude/man-got-everything-wanted-4txhk6
git checkout -b claude/man-got-everything-wanted-4txhk6 mio/claude/man-got-everything-wanted-4txhk6
```

Si `git fetch` falla por red, repítelo. Si pide usuario y contraseña, la
contraseña **no** es la de tu cuenta: es un token de
https://github.com/settings/tokens

Para comprobar que ha llegado:

```powershell
dir projects\hombre-que-lo-consiguio-todo\prueba.bat
```

Si te lo lista, ya lo tienes.

## 3. Hacer el vídeo

Entra en `projects\hombre-que-lo-consiguio-todo` y:

| Fichero | Qué hace |
|---|---|
| **`prueba.bat`** | Doble clic. Renderiza **solo los 2 primeros bloques** (~45 s). Para ver cómo queda antes de gastar el render entero. |
| **`completo.bat`** | Doble clic. Renderiza **los 12 bloques** y los une en un MP4 final. Tarda bastante. |

Se abre una ventana negra con el progreso. **No la cierres.** Cuando termine
pone `LISTO` y la ruta del vídeo, que sale en:

```
projects\hombre-que-lo-consiguio-todo\salida\hombre-que-lo-consiguio-todo.mp4
```

### Lo único que te va a preguntar

La primera vez, si `config.toml` no tiene clave de Pexels, la pide por pantalla:

```
Pega aquí tu clave de Pexels y pulsa Intro:
```

Pegas la clave, Intro, y no vuelve a preguntar nunca más. Se guarda en
`config.toml`, que está en `.gitignore`: **no se sube a GitHub**. Por eso no
está escrita dentro de ningún fichero del repo — si estuviera, quedaría
publicada en el historial para siempre.

### Lo que ya no hay que rellenar

Nada más. El script hace solo lo que antes había que pegar a mano:

- lee `guion.md` y genera el guion y las palabras clave;
- reparte el guion en 12 bloques, uno por tramo de la escaleta;
- pasa cada bloque a `cli.py` con su voz, su formato 16:9 y sus términos;
- une los 12 trozos en el MP4 final.

Ni tema, ni guion, ni términos, ni voz, ni formato. Ya va todo dentro.

---

## Si algo falla

El registro completo queda en `salida\registro.txt`. Mándamelo tal cual y
miramos qué ha pasado. En pantalla el motivo sale en los últimos mensajes,
antes del `Pulsa Intro para cerrar`.

## Dos cosas que conviene saber

**`curl` en PowerShell no es `curl`.** En PowerShell 5.1 (el que trae Windows)
`curl` es un alias de `Invoke-WebRequest` y no entiende `-H`. Si quieres probar
la clave de Pexels a mano, tiene que ser `curl.exe`:

```powershell
curl.exe -H "Authorization: TU_CLAVE" "https://api.pexels.com/v1/videos/search?query=city&per_page=1"
```

**No he podido comprobar la clave de Pexels ni la voz de Edge desde aquí.** El
entorno donde yo trabajo bloquea `api.pexels.com` y `speech.platform.bing.com`
(devuelven 403 en el proxy, comprobado desde dentro de la propia aplicación).
Eso es un límite de mi entorno, no un fallo de tu clave ni del programa: **no
sé si funcionan en tu ordenador porque no puedo probarlo**. En tu Windows, con
salida normal a internet, no hay ningún motivo conocido para que fallen, pero
hasta que lo lances no está confirmado.

## Alternativa sin scripts: la interfaz web

Si prefieres verlo con ratón, doble clic en `webui.bat` (está en la carpeta
raíz) y abre http://127.0.0.1:8501. Ahí los campos a rellenar son:

| Campo | Qué pones |
|---|---|
| **Pexels API Key** (en *Configuración básica*) | Tu clave |
| **Tema del vídeo** | `El hombre que lo consiguió todo` |
| **Guion del vídeo (opcional)** | El contenido de `guion.txt` |
| **Palabras clave del vídeo (inglés, opcional)** | El contenido de `terminos.txt` |
| **Voz (idioma del guion)** | `es-ES-AlvaroNeural-Male` |
| **Relación de aspecto del vídeo** | 16:9 |

Esta vía sí obliga a copiar y pegar, y además hace **una sola tarea** con el
guion entero, así que las imágenes no quedan pegadas a su tramo del guion. Los
`.bat` hacen un bloque por tramo, que es lo que queremos. Usa la web solo si
quieres trastear.
