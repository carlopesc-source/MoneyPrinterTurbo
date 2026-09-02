"""Renderiza usando las funciones reales del repo (video.py), con material local."""
import glob, os, shutil, sys, time
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, "/home/user/MoneyPrinterTurbo")

from app.models.schema import MaterialInfo, VideoAspect, VideoConcatMode, VideoParams
from app.services import video as V
from app.utils import utils

BASE = os.path.dirname(os.path.abspath(__file__))
CLIP = 6


def _una(ruta):
    r = V.preprocess_video([MaterialInfo(provider="local", url=ruta, duration=0)],
                           clip_duration=CLIP)
    return r[0].url if r else None


def main(limite=None, audio=None, srt=None, salida="demo.mp4"):
    destino = utils.storage_dir("local_videos", create=True)
    imgs = sorted(glob.glob(os.path.join(BASE, "daniel", "*.png")))
    if limite:
        imgs = imgs[:limite]
    mats = []
    for img in imgs:
        dst = os.path.join(destino, os.path.basename(img))
        if not os.path.exists(dst):
            shutil.copy2(img, dst)
        mats.append(MaterialInfo(provider="local", url=dst, duration=0))

    t0 = time.time()
    print(f"[1/3] preprocesando {len(mats)} imágenes -> clips", flush=True)
    # preprocess_video es secuencial y cada imagen tarda ~30 s; se reparte
    # entre procesos porque cada una escribe su propio fichero.
    with ProcessPoolExecutor(max_workers=4) as pool:
        listas = list(pool.map(_una, [m.url for m in mats]))
    mats = [MaterialInfo(provider="local", url=u, duration=0) for u in listas if u]
    print(f"      {len(mats)} clips válidos en {time.time()-t0:.0f}s", flush=True)

    params = VideoParams(
        video_subject="El hombre que lo consiguió todo",
        video_aspect=VideoAspect.landscape.value,
        video_clip_duration=CLIP,
        subtitle_enabled=True,
        subtitle_position="bottom",
        font_name="BeVietnamPro-Bold.ttf",
        font_size=52,
        text_fore_color="#FFFFFF",
        stroke_color="#000000",
        stroke_width=2.0,
        bgm_type="",
        n_threads=4,
    )

    combinado = os.path.join(BASE, "combinado.mp4")
    print("[2/3] montando clips contra la narración", flush=True)
    V.combine_videos(
        combined_video_path=combinado,
        video_paths=[m.url for m in mats],
        audio_file=audio,
        video_aspect=VideoAspect.landscape,
        video_concat_mode=VideoConcatMode.sequential,
        max_clip_duration=CLIP,
        threads=4,
    )
    print(f"      combinado en {time.time()-t0:.0f}s", flush=True)

    print("[3/3] quemando subtítulos y audio", flush=True)
    V.generate_video(
        video_path=combinado,
        audio_path=audio,
        subtitle_path=srt,
        output_file=os.path.join(BASE, salida),
        params=params,
    )
    print(f"LISTO: {os.path.join(BASE, salida)} en {time.time()-t0:.0f}s")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--limite", type=int)
    p.add_argument("--audio", default=os.path.join(BASE, "narracion.wav"))
    p.add_argument("--srt", default=os.path.join(BASE, "narracion.srt"))
    p.add_argument("--salida", default="demo.mp4")
    a = p.parse_args()
    main(a.limite, a.audio, a.srt, a.salida)
