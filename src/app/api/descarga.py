from fastapi import APIRouter
from fastapi.responses import FileResponse
from pathlib import Path
from fastapi import BackgroundTasks


from app.services.descarga.servicioDescarga import ServicioDescarga
from app.utils.archivos import eliminar_carpeta_temporal


router = APIRouter()

servicio = ServicioDescarga()


@router.get("/descarga")
async def descargar(url: str, formato: str, background_task: BackgroundTasks):

    ruta = servicio.descargar(url, formato)
    background_task.add_task(eliminar_carpeta_temporal, ruta)

    return FileResponse(
        path=ruta,
        filename=Path(ruta).name,
        media_type="application/octet-stream"
    )