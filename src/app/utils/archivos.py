from pathlib import Path
import shutil


def eliminar_carpeta_temporal(ruta_archivo: str):

    carpeta = Path(ruta_archivo).parent

    if carpeta.exists():
        shutil.rmtree(carpeta, ignore_errors=True)