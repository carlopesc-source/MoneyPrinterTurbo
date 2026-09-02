"""Narración offline con espeak-ng (la voz de Microsoft está bloqueada aquí).

Sintetiza frase a frase para saber la duración exacta de cada una y poder
escribir el SRT sin depender de Whisper.
"""
import ctypes, re, struct, wave
import espeakng_loader

RATE = 22050
_lib = None

CB = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(ctypes.c_short),
                      ctypes.c_int, ctypes.c_void_p)


def _init(velocidad=150, voz=b"es"):
    global _lib
    if _lib is not None:
        return _lib
    lib = ctypes.cdll.LoadLibrary(str(espeakng_loader.get_library_path()))
    lib.espeak_Initialize(1, 0, str(espeakng_loader.get_data_path()).encode(), 0)
    lib.espeak_SetVoiceByName(voz)
    lib.espeak_SetParameter(1, velocidad, 0)   # espeakRATE
    lib.espeak_SetParameter(2, 100, 0)         # volumen
    lib.espeak_SetParameter(5, 45, 0)          # tono
    _lib = lib
    return lib


def sintetizar(texto, velocidad=150):
    """Devuelve los samples PCM (bytes, mono 16 bit) de un fragmento."""
    lib = _init(velocidad)
    trozos = []

    @CB
    def cb(wav, n, ev):
        if wav and n > 0:
            trozos.append(ctypes.string_at(wav, n * 2))
        return 0

    lib.espeak_SetSynthCallback(cb)
    b = texto.encode("utf-8")
    lib.espeak_Synth(b, len(b) + 1, 0, 0, 0, 1, None, None)
    lib.espeak_Synchronize()
    return b"".join(trozos)


def trocear(texto, maximo=78):
    """Parte el guion en unidades de subtítulo."""
    fuera = []
    for parrafo in [p.strip() for p in texto.split("\n") if p.strip()]:
        for frase in re.split(r"(?<=[.:;?!])\s+", parrafo):
            frase = frase.strip()
            if not frase:
                continue
            while len(frase) > maximo:
                corte = frase.rfind(" ", 0, maximo)
                if corte < maximo * 0.5:
                    corte = maximo
                fuera.append(frase[:corte].strip())
                frase = frase[corte:].strip()
            if frase:
                fuera.append(frase)
    return fuera


def _ts(s):
    h, r = divmod(s, 3600)
    m, r = divmod(r, 60)
    seg, ms = divmod(r, 1)
    return f"{int(h):02d}:{int(m):02d}:{int(seg):02d},{int(ms*1000):03d}"


def narrar(texto, wav_path, srt_path, velocidad=150, pausa=0.30):
    piezas = trocear(texto)
    silencio = b"\x00\x00" * int(RATE * pausa)
    pcm, srt, t = [], [], 0.0
    for i, frase in enumerate(piezas, 1):
        datos = sintetizar(frase, velocidad)
        dur = len(datos) / 2 / RATE
        srt.append(f"{i}\n{_ts(t)} --> {_ts(t + dur)}\n{frase}\n")
        pcm.append(datos)
        pcm.append(silencio)
        t += dur + pausa
    with wave.open(wav_path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(pcm))
    open(srt_path, "w", encoding="utf-8").write("\n".join(srt))
    return t, len(piezas)


if __name__ == "__main__":
    import sys
    texto = open(sys.argv[1], encoding="utf-8").read()
    dur, n = narrar(texto, sys.argv[2], sys.argv[3])
    print(f"duración: {dur:.1f}s ({dur/60:.2f} min), {n} subtítulos")
