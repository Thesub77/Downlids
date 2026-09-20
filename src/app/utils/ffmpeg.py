import shutil
from pathlib import Path


def obtener_ruta_ffmpeg() -> str:
    """
    Retorna la ruta al ejecutable de FFmpeg.
    Primero busca en el PATH del sistema; si no se encuentra,
    utiliza el ejecutable empaquetado por imageio_ffmpeg.
    """
    ruta_sistema = shutil.which("ffmpeg")
    if ruta_sistema:
        return ruta_sistema

    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"
