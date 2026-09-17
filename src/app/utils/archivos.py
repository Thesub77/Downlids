import time
from pathlib import Path
import shutil


def eliminar_carpeta_temporal(ruta_archivo: str | Path):
    ruta = Path(ruta_archivo)
    carpeta = ruta if ruta.is_dir() else ruta.parent

    if not carpeta.exists():
        return

    for _ in range(3):
        try:
            shutil.rmtree(carpeta)
            break
        except Exception:
            time.sleep(0.2)