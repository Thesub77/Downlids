from fastapi import APIRouter, HTTPException

from app.models.metadatos import (
    SolicitudMetadatos,
    RespuestaMetadatos
)

from app.services.metadatos.servicioMetadatos import ServicioMetadatos

router = APIRouter(
    prefix="/metadata",
    tags=["Metadata"]
)

servicio = ServicioMetadatos()


@router.post("/metadatos", response_model=RespuestaMetadatos)
def obtener_metadatos(solicitud: SolicitudMetadatos):
    try:
        return servicio.obtener_metadatos(
            str(solicitud.url),
            solicitud.plataforma,
            cookies=solicitud.cookies
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        mensaje = str(e)
        if "members-only" in mensaje or "available to this channel's members" in mensaje:
            detalle = "Este video es exclusivo para miembros del canal y no está disponible públicamente."
        elif "Private video" in mensaje or "video is private" in mensaje:
            detalle = "Este video es privado y no se puede acceder a su contenido."
        elif "Video unavailable" in mensaje or "This video is unavailable" in mensaje:
            detalle = "El video no se encuentra disponible o el enlace no es válido."
        elif any(ig_err in mensaje for ig_err in [
            "Instagram API is not granting access",
            "empty media response",
            "login-required",
            "checkpoint_required",
            "Please log in"
        ]):
            detalle = "Esta publicación o Reel de Instagram es privado o requiere inicio de sesión para acceder."
        elif "Telegram bloqueó" in mensaje or "Restringir guardar contenido" in mensaje or "restricciones de contenido" in mensaje or "protección contra copias" in mensaje:
            detalle = mensaje
        elif any(tg_err in mensaje for tg_err in [
            "Extractor telegram:embed returned nothing",
            "telegram:embed",
            "No fue posible encontrar un video público",
            "No se encontró información o video en el enlace"
        ]):
            detalle = (
                "No fue posible acceder al video de Telegram. "
                "Telegram no utiliza sesiones web basadas en cookies HTTP (funciona mediante su protocolo nativo MTProto en WebSockets/IndexedDB). "
                "Por esa razón, solo videos públicos accesibles sin restricciones en la web pueden extraerse. "
                "Si el grupo/canal tiene activado 'Restringir guardar contenido' (noforwards), es un tema privado o el video se subió como archivo/documento, Telegram no permite la descarga web."
            )
        elif any(fb_err in mensaje for fb_err in [
            "Cannot parse data",
            "[facebook]",
            "facebook.com",
            "logged in users",
            "Log in to Facebook"
        ]):
            detalle = "Facebook no permitió acceder a este video de forma anónima (requiere sesión o es privado). Si utilizas la extensión Downlids Companion con tu sesión de Facebook activa, o colocas un archivo 'cookies.txt' en el servidor, podrás descargarlo."
        else:
            detalle = f"No fue posible obtener los metadatos: {mensaje}"

        raise HTTPException(
            status_code=400,
            detail=detalle
        )