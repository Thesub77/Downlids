from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from app.services.descarga.servicioDescarga import ServicioDescarga
from app.utils.archivos import eliminar_carpeta_temporal


router = APIRouter()

servicio = ServicioDescarga()


@router.get("/descarga")
def descargar(url: str, formato: str, plataforma: str | None = None):
    try:
        ruta = servicio.descargar(url, formato, plataforma)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar la descarga: {str(e)}"
        )

    return FileResponse(
        path=ruta,
        filename=Path(ruta).name,
        media_type="application/octet-stream",
        background=BackgroundTask(eliminar_carpeta_temporal, ruta)
    )