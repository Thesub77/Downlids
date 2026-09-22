import time
import uuid
import threading
from pathlib import Path

from app.core.config import MAX_DOWNLOAD_SIZE_BYTES, MAX_DOWNLOAD_SIZE_MB
from app.services.metadatos.ytdlpAdaptador import YtdlpAdaptador
from app.services.metadatos.validadorURL import ValidadorURL
from app.utils.archivos import eliminar_carpeta_temporal


class ServicioDescarga:

    def __init__(self):
        self.adapter = YtdlpAdaptador()
        self.validador = ValidadorURL()
        self._descargas: dict[str, dict] = {}
        self._lock = threading.Lock()

    def descargar(self, url: str, formato: str, plataforma: str | None = None) -> str:
        """Descarga síncrona directa (retrocompatibilidad)."""
        self.validador.validar(url, plataforma)

        return self.adapter.descargar_video(
            url=url,
            formato=formato
        )

    def iniciar_descarga(self, url: str, formato: str, plataforma: str | None = None) -> str:
        """Inicia una tarea de descarga asíncrona con seguimiento de progreso en tiempo real."""
        self.validador.validar(url, plataforma)
        self._limpiar_expiradas()

        download_id = str(uuid.uuid4())
        registro = {
            "id": download_id,
            "url": url,
            "formato": formato,
            "plataforma": plataforma,
            "estado": "iniciando",  # iniciando, descargando, procesando, completado, error
            "progreso": 0.0,
            "velocidad": "",
            "eta": "",
            "ruta_archivo": None,
            "nombre_archivo": None,
            "error": None,
            "creado_en": time.time(),
        }

        with self._lock:
            self._descargas[download_id] = registro

        hilo = threading.Thread(
            target=self._ejecutar_descarga,
            args=(download_id, url, formato),
            daemon=True
        )
        hilo.start()

        return download_id

    def _ejecutar_descarga(self, download_id: str, url: str, formato: str):
        def hook_progreso(d: dict):
            status = d.get("status")
            with self._lock:
                registro = self._descargas.get(download_id)
                if not registro:
                    return

                if status == "downloading":
                    descargado = d.get("downloaded_bytes") or 0
                    if descargado > MAX_DOWNLOAD_SIZE_BYTES:
                        raise ValueError(f"La descarga ha superado el límite permitido de {MAX_DOWNLOAD_SIZE_MB} MB.")

                    total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                    progreso = 0.0
                    if total > 0:
                        progreso = round((descargado / total) * 100, 1)
                    else:
                        pct_str = d.get("_percent_str", "").replace("%", "").strip()
                        try:
                            progreso = float(pct_str)
                        except Exception:
                            progreso = 0.0

                    registro["estado"] = "descargando"
                    registro["progreso"] = progreso
                    registro["velocidad"] = (d.get("_speed_str") or "").strip()
                    registro["eta"] = (d.get("_eta_str") or "").strip()

                elif status == "finished":
                    registro["estado"] = "procesando"
                    registro["progreso"] = 100.0
                    registro["velocidad"] = ""
                    registro["eta"] = ""

        try:
            ruta = self.adapter.descargar_video(url, formato, hook_progreso=hook_progreso)
            with self._lock:
                registro = self._descargas.get(download_id)
                if registro:
                    registro["estado"] = "completado"
                    registro["progreso"] = 100.0
                    registro["ruta_archivo"] = ruta
                    registro["nombre_archivo"] = Path(ruta).name
        except Exception as e:
            with self._lock:
                registro = self._descargas.get(download_id)
                if registro:
                    registro["estado"] = "error"
                    registro["error"] = str(e)

    def obtener_estado(self, download_id: str) -> dict | None:
        """Consulta el estado, progreso, velocidad y ETA de la descarga."""
        with self._lock:
            registro = self._descargas.get(download_id)
            if not registro:
                return None
            return {
                "id": registro["id"],
                "estado": registro["estado"],
                "progreso": registro["progreso"],
                "velocidad": registro["velocidad"],
                "eta": registro["eta"],
                "nombre_archivo": registro["nombre_archivo"],
                "error": registro["error"]
            }

    def obtener_archivo(self, download_id: str) -> tuple[str, str]:
        """Obtiene la ruta y nombre del archivo descargado."""
        with self._lock:
            registro = self._descargas.get(download_id)

        if not registro:
            raise KeyError("Identificador de descarga no encontrado o expirado.")

        if registro["estado"] == "error":
            raise RuntimeError(registro["error"] or "Error al procesar la descarga.")

        if registro["estado"] != "completado" or not registro["ruta_archivo"]:
            raise ValueError(f"La descarga aún no ha finalizado (estado actual: {registro['estado']}).")

        return registro["ruta_archivo"], registro["nombre_archivo"]

    def limpiar_descarga(self, download_id: str):
        """Elimina los archivos temporales de la descarga completada o fallida."""
        with self._lock:
            registro = self._descargas.pop(download_id, None)

        if registro and registro.get("ruta_archivo"):
            eliminar_carpeta_temporal(registro["ruta_archivo"])

    def _limpiar_expiradas(self, ttl_segundos: int = 1800):
        ahora = time.time()
        expiradas = []
        with self._lock:
            for did, reg in list(self._descargas.items()):
                if ahora - reg["creado_en"] > ttl_segundos:
                    expiradas.append((did, reg.get("ruta_archivo")))
                    del self._descargas[did]

        for _, ruta in expiradas:
            if ruta:
                eliminar_carpeta_temporal(ruta)
