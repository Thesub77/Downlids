from pathlib import Path

# Raíz del proyecto
BASE_DIR = Path(__file__).resolve().parents[3]

# Directorios principales
SRC_DIR = BASE_DIR / "src"
APP_DIR = SRC_DIR / "app"

STATIC_DIR = APP_DIR / "static"
TEMPLATES_DIR = APP_DIR / "templates"
DOWNLOADS_DIR = BASE_DIR / "downloads"

DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Configuración de la aplicación
APP_NAME = "Downlids"
APP_VERSION = "0.1.0"
MAX_DOWNLOAD_SIZE_MB = 1024
MAX_DOWNLOAD_SIZE_BYTES = MAX_DOWNLOAD_SIZE_MB * 1024 * 1024
SUPPORTED_PLATFORMS = [
    "YouTube",
    "TikTok",
    "Instagram",
    "Twitch",
    "Kick",
    "Vimeo",
    "Desconocida"
]