import unittest
from pathlib import Path
from fastapi import HTTPException

from app.api.descarga import descargar
from app.utils.archivos import eliminar_carpeta_temporal
from app.utils.ffmpeg import obtener_ruta_ffmpeg
from app.services.metadatos.servicioMetadatos import ServicioMetadatos


class TestDescarga(unittest.TestCase):

    def test_ffmpeg_disponible(self):
        ruta_ffmpeg = obtener_ruta_ffmpeg()
        self.assertTrue(bool(ruta_ffmpeg))
        self.assertTrue(Path(ruta_ffmpeg).exists() or ruta_ffmpeg == "ffmpeg")

    def test_eliminar_carpeta_temporal(self):
        import tempfile
        carpeta = Path(tempfile.mkdtemp())
        archivo = carpeta / "video.mp4"
        archivo.write_text("dummy video content")

        self.assertTrue(archivo.exists())
        self.assertTrue(carpeta.exists())

        eliminar_carpeta_temporal(str(archivo))

        self.assertFalse(archivo.exists())
        self.assertFalse(carpeta.exists())

    def test_metadatos_multiples_calidades(self):
        servicio = ServicioMetadatos()
        meta = servicio.obtener_metadatos("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertTrue(len(meta.formatos) > 2)

        # Verificar que el primer formato sea audio
        self.assertEqual(meta.formatos[0].id, "bestaudio")

        # Verificar que los formatos de video estén presentes y ordenados
        calidades = [f.calidad for f in meta.formatos[1:]]
        self.assertTrue(any("1080p" in c for c in calidades))
        self.assertTrue(any("720p" in c for c in calidades))

    def test_descarga_exitosa_y_cleanup(self):
        response = descargar(
            url="https://www.youtube.com/watch?v=jNQXAC9IVRw",
            formato="18"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.background)

        ruta = Path(response.path)
        self.assertTrue(ruta.exists())
        carpeta = ruta.parent
        self.assertTrue(carpeta.exists())

        # Ejecutamos la tarea de fondo directamente tal como lo hace Starlette al terminar el envio
        import asyncio
        asyncio.run(response.background())

        # Comprobamos que la carpeta y el archivo han sido completamente eliminados
        self.assertFalse(ruta.exists())
        self.assertFalse(carpeta.exists())

    def test_descarga_audio_bestaudio(self):
        response = descargar(
            url="https://www.youtube.com/watch?v=jNQXAC9IVRw",
            formato="bestaudio"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.path.endswith(".m4a") or response.path.endswith(".mp3"))

        ruta = Path(response.path)
        self.assertTrue(ruta.exists())

        import asyncio
        asyncio.run(response.background())
        self.assertFalse(ruta.exists())


if __name__ == "__main__":
    unittest.main()
