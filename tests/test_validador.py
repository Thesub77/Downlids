# Para la ejecución de este test se debe especificar la carpeta raíz del código fuente (src) en PYTHONPATH:
# PowerShell: $env:PYTHONPATH="src"; uv run python -m unittest tests/test_validador.py
# Bash:       PYTHONPATH=src uv run python -m unittest tests/test_validador.py

import unittest
from app.models.metadatos import Plataforma, SolicitudMetadatos
from app.services.metadatos.validadorURL import ValidadorURL
from app.api.metadatos import obtener_metadatos
from fastapi import HTTPException


class TestValidadorURL(unittest.TestCase):

    def setUp(self):
        self.validador = ValidadorURL()

    def test_identificar_youtube(self):
        urls_youtube = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/dQw4w9WgXcQ",
            "www.youtube.com/watch?v=dQw4w9WgXcQ",
            "youtu.be/dQw4w9WgXcQ",
        ]
        for url in urls_youtube:
            with self.subTest(url=url):
                self.assertEqual(self.validador.identificar_plataforma(url), Plataforma.YOUTUBE)

    def test_identificar_tiktok(self):
        urls_tiktok = [
            "https://www.tiktok.com/@usuario/video/7106594312292453678",
            "https://vm.tiktok.com/ZMJaV1x6E/",
            "https://vt.tiktok.com/ZSJaV1x6E/",
            "https://m.tiktok.com/v/7106594312292453678.html",
            "www.tiktok.com/@usuario/video/7106594312292453678",
            "vm.tiktok.com/ZMJaV1x6E/",
        ]
        for url in urls_tiktok:
            with self.subTest(url=url):
                self.assertEqual(self.validador.identificar_plataforma(url), Plataforma.TIKTOK)

    def test_identificar_instagram(self):
        urls_instagram = [
            "https://www.instagram.com/reel/C1234567890/",
            "https://www.instagram.com/p/C1234567890/",
            "https://www.instagram.com/tv/C1234567890/",
            "https://instagr.am/p/C1234567890/",
            "instagram.com/reel/C1234567890/",
        ]
        for url in urls_instagram:
            with self.subTest(url=url):
                self.assertEqual(self.validador.identificar_plataforma(url), Plataforma.INSTAGRAM)

    def test_identificar_desconocida(self):
        urls_desconocidas = [
            "https://example.com/video",
            "https://fake-tiktok.com/video",
            "https://notyoutube.com/watch",
            "https://twitter.com/usuario/status/123",
        ]
        for url in urls_desconocidas:
            with self.subTest(url=url):
                self.assertEqual(
                    self.validador.identificar_plataforma(url),
                    Plataforma.DESCONOCIDA
                )

    def test_validar_coincidencia_correcta(self):
        self.assertEqual(
            self.validador.validar("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "youtube"),
            Plataforma.YOUTUBE
        )
        self.assertEqual(
            self.validador.validar("https://www.tiktok.com/@user/video/123", "tiktok"),
            Plataforma.TIKTOK
        )
        self.assertEqual(
            self.validador.validar("https://vm.tiktok.com/ZM123/", "tiktok"),
            Plataforma.TIKTOK
        )
        self.assertEqual(
            self.validador.validar("https://www.instagram.com/reel/C1234567890/", "instagram"),
            Plataforma.INSTAGRAM
        )
        self.assertEqual(
            self.validador.validar("https://instagr.am/p/C1234567890/", "ig"),
            Plataforma.INSTAGRAM
        )

    def test_validar_coincidencia_incorrecta(self):
        # Enlace de YouTube cuando se seleccionó TikTok
        with self.assertRaises(ValueError) as ctx:
            self.validador.validar("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "tiktok")
        self.assertIn("no coincide con la plataforma seleccionada (TikTok)", str(ctx.exception))

        # Enlace de TikTok cuando se seleccionó YouTube
        with self.assertRaises(ValueError) as ctx:
            self.validador.validar("https://www.tiktok.com/@user/video/123", "youtube")
        self.assertIn("no coincide con la plataforma seleccionada (YouTube)", str(ctx.exception))

        # Enlace de Instagram cuando se seleccionó YouTube
        with self.assertRaises(ValueError) as ctx:
            self.validador.validar("https://www.instagram.com/reel/C1234567890/", "youtube")
        self.assertIn("no coincide con la plataforma seleccionada (YouTube)", str(ctx.exception))

        # Enlace de YouTube cuando se seleccionó Instagram
        with self.assertRaises(ValueError) as ctx:
            self.validador.validar("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "instagram")
        self.assertIn("no coincide con la plataforma seleccionada (Instagram)", str(ctx.exception))

    def test_validar_url_vacia(self):
        with self.assertRaises(ValueError) as ctx:
            self.validador.validar("   ", "youtube")
        self.assertIn("no puede estar vacía", str(ctx.exception))

    def test_endpoint_rechaza_plataforma_invalida(self):
        # Solicitud al endpoint con YouTube URL y plataforma TikTok seleccionada
        solicitud_yt = SolicitudMetadatos(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            plataforma="tiktok"
        )
        with self.assertRaises(HTTPException) as ctx:
            obtener_metadatos(solicitud_yt)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("no coincide con la plataforma seleccionada (TikTok)", ctx.exception.detail)

        # Solicitud al endpoint con TikTok URL y plataforma YouTube seleccionada
        solicitud_tt = SolicitudMetadatos(
            url="https://www.tiktok.com/@usuario/video/7106594312292453678",
            plataforma="youtube"
        )
        with self.assertRaises(HTTPException) as ctx:
            obtener_metadatos(solicitud_tt)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("no coincide con la plataforma seleccionada (YouTube)", ctx.exception.detail)

        # Solicitud al endpoint con Instagram URL y plataforma YouTube seleccionada
        solicitud_ig = SolicitudMetadatos(
            url="https://www.instagram.com/reel/C1234567890/",
            plataforma="youtube"
        )
        with self.assertRaises(HTTPException) as ctx:
            obtener_metadatos(solicitud_ig)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("no coincide con la plataforma seleccionada (YouTube)", ctx.exception.detail)

    def test_descarga_rechaza_plataforma_invalida(self):
        from app.api.descarga import descargar

        # Intento de descarga de TikTok con plataforma YouTube
        with self.assertRaises(HTTPException) as ctx:
            descargar(
                url="https://www.tiktok.com/@usuario/video/7106594312292453678",
                formato="mp4",
                plataforma="youtube"
            )
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("no coincide con la plataforma seleccionada (YouTube)", ctx.exception.detail)

        # Intento de descarga de Instagram con plataforma YouTube
        with self.assertRaises(HTTPException) as ctx:
            descargar(
                url="https://www.instagram.com/reel/C1234567890/",
                formato="mp4",
                plataforma="youtube"
            )
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("no coincide con la plataforma seleccionada (YouTube)", ctx.exception.detail)


if __name__ == "__main__":
    unittest.main()

