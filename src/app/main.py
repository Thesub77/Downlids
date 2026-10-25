from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.inicio import router as home_router
from app.api.metadatos import router as metadatos_router
from app.api.descarga import router as descarga_router
from app.core.config import STATIC_DIR
from app.core.config import APP_NAME
from app.core.config import APP_VERSION



from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_private_network=True,
)


@app.middleware("http")
async def no_cache_static_middleware(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


@app.get("/api/estado")
async def estado_servidor():
    return {
        "estado": "activo",
        "nombre": APP_NAME,
        "version": APP_VERSION
    }


app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)

app.include_router(home_router)
app.include_router(metadatos_router)
app.include_router(descarga_router)