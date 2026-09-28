from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from starlette.background import BackgroundTask

from app.services.descarga.servicioDescarga import ServicioDescarga
from app.utils.archivos import eliminar_carpeta_temporal


router = APIRouter()

servicio = ServicioDescarga()


class SolicitudDescarga(BaseModel):
    url: str
    formato: str
    plataforma: str | None = None


@router.post("/descarga/iniciar")
def iniciar_descarga(solicitud: SolicitudDescarga):
    try:
        download_id = servicio.iniciar_descarga(
            url=solicitud.url,
            formato=solicitud.formato,
            plataforma=solicitud.plataforma
        )
        return {"download_id": download_id}
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al iniciar la descarga: {str(e)}"
        )


@router.get("/descarga/estado/{download_id}")
def obtener_estado(download_id: str):
    estado = servicio.obtener_estado(download_id)
    if not estado:
        raise HTTPException(
            status_code=404,
            detail="Descarga no encontrada o expirada."
        )
    return estado


@router.get("/descarga/archivo/{download_id}")
def descargar_archivo(download_id: str):
    try:
        ruta, nombre = servicio.obtener_archivo(download_id)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail="Descarga no encontrada o expirada."
        )
    except ValueError as e:
        raise HTTPException(
            status_code=409,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al entregar archivo: {str(e)}"
        )

    return FileResponse(
        path=ruta,
        filename=nombre,
        media_type="application/octet-stream",
        background=BackgroundTask(servicio.limpiar_descarga, download_id)
    )


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